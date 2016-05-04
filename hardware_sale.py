#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, render_template, flash
from datetime import datetime, timedelta
from common import app, query_db, get_sale_name_by_sale_id, get_device_name_by_device_id, get_sale_date_by_sale_id, \
                   is_admin, add_new_admin, get_extended_device_details_by_sale_device_id, get_user_id_by_user_email, \
                   get_sale_details_by_sale_id, get_device_details_by_device_id, generate_uuid, send_email, get_sale_device_id, \
                   insert_to_db, check_auth, get_device_name_and_sale_name_by_sale_device_id, delete_from_db, get_hash_of_project, \
                   get_bucket_list, debug


@app.route('/')
def show_active_sales():
    sales = query_db('select sale_id, sale_name, sale_date, active from tbl_sale where active=1')
    if len(sales) == 1:
        return redirect(url_for('show_sale', sale_id=sales[0][0]))
    return render_template('show_active_sales.html', sales=sales,projecthash=get_hash_of_project())


@app.route('/sale/<int:sale_id>')
def show_sale(sale_id):
    sale_name = get_sale_name_by_sale_id(sale_id)
    sale_date = query_db("select sale_date from tbl_sale where sale_id=%s" % sale_id)[0][0]
    sale_details = query_db('select sd.device_id, sd.quantity, d.device_name, d.device_description, t.type_name, count(user_sale_device_id), d.price from tbl_sale_device sd join tbl_device d on sd.device_id=d.device_id join tbl_type t on d.type_id=t.type_id left join tbl_user_sale_device usd on usd.sale_device_id=sd.sale_device_id where sd.sale_id=%s group by device_id' % sale_id)
    return render_template('show_sale_details.html', sale_id=sale_id,sale_name=sale_name,sale_details=sale_details,sale_date=sale_date,projecthash=get_hash_of_project())


@app.route('/bucket/<int:sale_id>/<int:device_id>')
def request_add_to_bucket(sale_id, device_id):
    device_name = get_device_name_by_device_id(device_id)
    sale_name = get_sale_name_by_sale_id(sale_id)
    sale_date = get_sale_date_by_sale_id(sale_id)
    close_date = sale_date + timedelta(hours=24)
    return render_template('request_add_to_bucket.html', sale_id=sale_id,sale_name=sale_name,device_id=device_id,device_name=device_name,sale_date=sale_date,close_date=close_date,projecthash=get_hash_of_project())


@app.route('/add_admin', methods=['POST'])
def add_admin():
    (admin_name, admin_email, plaintext_password) = (request.form['admin_name'], request.form['admin_email'], request.form['plaintext_password'])
    if not is_admin(admin_name):
        if add_new_admin(admin_name, admin_email, plaintext_password):
            flash("Admin %s successfully added." % admin_name)
        else:
            flash("Error adding new admin %s.  Check logs for details." % admin_name, "error")
    else:
        flash("Admin %s already exists." % admin_name, "error")
    return redirect(url_for('admin_page'))


@app.route('/sale_report/<int:sale_id>')
def sale_report(sale_id):
    sale_devices = query_db("select sale_device_id from tbl_sale_device where sale_id=%s" % sale_id)
    sale_name = get_sale_name_by_sale_id(sale_id)
    sale_reports = []
    for sale_device in sale_devices:
        sale_device_id = sale_device[0]
        device_id = query_db("select device_id from tbl_sale_device where sale_device_id=%s" % sale_device_id)[0][0]
        device_details = get_extended_device_details_by_sale_device_id(sale_device_id)
        user_emails = query_db("select u.user_email from tbl_user u join tbl_user_sale_device usd on u.user_id = usd.user_id where usd.won = 1 and usd.sale_device_id = %s order by u.user_email" % sale_device_id)
        user_names = []
        for user_email in user_emails:
            user_names.append(' '.join(map(str.capitalize, user_email[0].split('@')[0].split('.'))))
        sale_reports.append((device_details, user_names))
    return render_template('sale_report.html', sale_reports=sale_reports, sale_name=sale_name,projecthash=get_hash_of_project())


@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    user_email = request.form['user_email']
    device_id = request.form['device_id']
    sale_id = request.form['sale_id']
    if "viawest.com" not in user_email:
        flash("You must use your viawest.com email address.", "error")
        return redirect(url_for('show_sale', sale_id=sale_id))
    user_id = get_user_id_by_user_email(user_email)
    user_already_in_bucket = query_db("select count(usd.user_id) from tbl_user_sale_device usd join tbl_sale_device sd on usd.sale_device_id=sd.sale_device_id where sd.sale_id=%s and sd.device_id=%s and usd.user_id=%s" % (sale_id, device_id, user_id))[0][0]
    if user_already_in_bucket > 0:
        device_name = get_device_name_by_device_id(device_id)
        sale_name = get_sale_name_by_sale_id(sale_id)
        flash("There is already an entry for you under the bucket for a %s in %s" % (device_name, sale_name), "error")
        return redirect(url_for('show_sale', sale_id=sale_id))
    (sale_name, sale_date) = get_sale_details_by_sale_id(sale_id)
    (device_name, device_description, price) = get_device_details_by_device_id(device_id)
    uuid = generate_uuid()

    send_email(render_template('confirm_email.html', sale_name=sale_name, sale_date=sale_date, device_name=device_name, device_description=device_description, price=price, sale_id=sale_id, uuid=uuid), user_email)

    sale_device_id = get_sale_device_id(device_id, sale_id)
    query = "insert into tbl_user_uuid(user_id, uuid, sale_device_id) values(%s, '%s', %s)" % (user_id, uuid, sale_device_id)
    insert_to_db(query)
    flash("Please check your email for a verification link to add your name to the bucket for the %s" % device_name)
    return redirect(url_for('show_sale', sale_id=sale_id))


@app.route('/confirm/<sale_id>/<uuid>')
def confirm_bucket(sale_id, uuid):
    query = "select count(*), user_id, sale_device_id from tbl_user_uuid where uuid='%s'" % uuid
    (uuid_count, user_id, sale_device_id) = query_db(query)[0]
    if uuid_count != 1:
        flash("Sorry, this link UUID is not found.  Please try again.", "error")
        return redirect(url_for('show_active_sales'))
    (device_name, sale_name) = get_device_name_and_sale_name_by_sale_device_id(sale_device_id)
    try:
        insert_to_db("insert into tbl_user_sale_device(user_id, sale_device_id) values(%s, %s)" % (user_id, sale_device_id))
        flash("Your email address has been put into the bucket for a %s in %s" % (device_name, sale_name))
    except:
        flash("There is already an entry for you under the bucket for a %s in %s" % (device_name, sale_name), "error")
    finally:
        delete_from_db("delete from tbl_user_uuid where uuid='%s'" % uuid)
        return redirect(url_for('show_sale', sale_id=sale_id))


@app.route('/bucket_list/<sale_id>', methods=['GET', 'POST'])
def request_bucket_list(sale_id):
    if request.method == 'POST':
        user_email = request.form['user_email']
        items = get_bucket_list(user_email, sale_id)
        (sale_name, sale_date) = get_sale_details_by_sale_id(sale_id)
        send_email(render_template('send_bucket_list.html', items=items,sale_name=sale_name,sale_date=sale_date), user_email)
        flash("Your bucket list will be sent to %s" % user_email)
        return redirect(url_for('show_sale', sale_id=sale_id))
    else:
        sale_name = get_sale_name_by_sale_id(sale_id)
        return render_template('request_bucket_list.html', sale_name=sale_name,projecthash=get_hash_of_project())



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        admin_name = request.form['username']
        plaintext_password = request.form['password']    
        if check_auth(admin_name, plaintext_password):
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('admin_page'))
        error = 'Invalid username and/or password'
    return render_template('login.html', error=error,projecthash=get_hash_of_project())


@app.route('/admin')
def admin_page():
    if not session['logged_in']:
        return redirect(url_for('login'))
    sale_details = query_db("select sale_id, sale_name, sale_date from tbl_sale")
    admin_details = query_db("select admin_id, admin_name, admin_email from tbl_admin")
    return render_template('admin_page.html', sale_details=sale_details, admin_details=admin_details,projecthash=get_hash_of_project())


@app.route('/add_sale', methods=['POST'])
def add_sale():
    return "Not yet implemented"


@app.route('/delete_sale/<int:sale_id>')
def delete_sale(sale_id):
    return "Not yet implemented"


@app.route('/edit_sale/<int:sale_id>')
def edit_sale(sale_id):
    sale_name = get_sale_name_by_sale_id(sale_id)
    sale_details = query_db('select sd.device_id, sd.quantity, d.device_name, d.device_description, t.type_name, count(user_sale_device_id), d.price from tbl_sale_device sd join tbl_device d on sd.device_id=d.device_id join tbl_type t on d.type_id=t.type_id left join tbl_user_sale_device usd on usd.sale_device_id=sd.sale_device_id where sd.sale_id=%s group by device_id' % sale_id)
    return render_template('edit_sale.html', sale_id=sale_id,sale_name=sale_name,sale_details=sale_details,projecthash=get_hash_of_project())


@app.route('/show_bucket/<int:sale_id>/<int:device_id>')
def show_bucket(sale_id, device_id):
    bucket_members = query_db("select u.user_id, u.user_email from tbl_user u join tbl_user_sale_device usd on usd.user_id = u.user_id join tbl_sale_device sd on sd.sale_device_id = usd.sale_device_id where sd.sale_id = %s and sd.device_id = %s order by u.user_email" % (sale_id, device_id))
    sale_name = get_sale_name_by_sale_id(sale_id) 
    device_name = get_device_name_by_device_id(device_id)
    return render_template('show_bucket.html', sale_id=sale_id,device_name=device_name,sale_name=sale_name,bucket_members=bucket_members,projecthash=get_hash_of_project())


@app.route('/remove_device_from_sale/<int:sale_id>/<int:device_id>')
def remove_device_from_sale(sale_id, device_id, methods=['POST','GET']):
    if request.method == 'POST':
        sale_device_id = get_sale_device_id(device_id, sale_id)
        delete_from_db("delete from tbl_sale_device where sale_device_id=%s" % sale_device_id)
        return redirect( url_for('show_sale', sale_id=sale_id))
    message = "Are you sure you want to remove the %s from %s?" % (get_device_name_by_device_id(device_id), get_sale_name_by_sale_id(sale_id))
    return render_template('confirm_delete.html', message=message,name1="sale_id",value1=sale_id,name2="device_id",value2=device_id,projecthash=get_hash_of_project())


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_active_sales'))
