#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import sys
import smtplib
import uuid
import base64
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, g
from datetime import datetime
from bcrypt import hashpw, gensalt
from config import params


app = Flask(__name__)
app.config.update(params)
app.secret_key = app.config['SECRET_KEY']


def deactivate_sale(sale_id):
    debug("Deactivating sale %s" % sale_id)
    update_db("update tbl_sale set active=0 where sale_id=%s" % sale_id)


def update_admin_password(admin_name, plaintext_password):
    debug("Updating password for admin %s" % admin_name)
    if is_admin(admin_name):
        hashed_password = hashpw(plaintext_password, gensalt())
        update_db("update tbl_admin set hashed_password='%s' where admin_name=%s" % (hashed_password, admin_name))
        return True
    return False


def is_admin(admin_name):
    admin_exists = query_db("select count(admin_id) from tbl_admin where admin_name='%s'" % admin_name)[0][0]
    if admin_exists > 0:
        return True
    else:
        return False


def connect_db():
    con = None
    try:
        con = MySQLdb.connect(app.config['HOSTNAME'], app.config['USERNAME'], \
            app.config['PASSWORD'], app.config['DATABASE']);
    except MySQLdb.Error, e:
        debug("Error %d: %s" % (e.args[0],e.args[1]))
    finally:    
        return con


def insert_to_db(query):
    db = do_query(query)[0]
    db.commit()


delete_from_db = insert_to_db
update_db = insert_to_db


def query_db(query):
    cur = do_query(query)[1]
    return cur.fetchall()


def do_query(query):
    db = connect_db()
    cur = db.cursor()
    cur.execute(query)
    return (db, cur)


def get_sale_name_by_sale_id(sale_id):
    return query_db('select sale_name from tbl_sale where sale_id=%s' % sale_id)[0][0]


def get_sale_date_by_sale_id(sale_id):
    return query_db('select sale_date from tbl_sale where sale_id=%s' % sale_id)[0][0]


def get_device_name_by_device_id(device_id):
    return query_db('select device_name from tbl_device where device_id=%s' % device_id)[0][0]


def get_sale_device_id(device_id, sale_id):
    return query_db("select sale_device_id from tbl_sale_device where device_id=%s and sale_id=%s" % (device_id, sale_id))[0][0]


def send_email(html, user_email, subject):
    msg = MIMEMultipart('alternative')
    part1 = MIMEText(html, 'html')
    msg['Subject'] = "INetU Hardware Sale: %s" % subject
    msg['From'] = app.config['LOCAL_SENDER']
    msg['To'] = user_email
    msg.attach(part1)
    s = smtplib.SMTP('localhost')
    s.sendmail(app.config['LOCAL_SENDER'], user_email, msg.as_string())
    s.quit()


def get_bucket_count(device_id, sale_id):
    bucket_count = query_db("select count(sale_device_id) from tbl_sale_device where device_id=%s and sale_id=%s" % (device_id, sale_id))[0][0]
    return bucket_count


def get_user_id_by_user_email(user_email):
    result = query_db("select user_id from tbl_user where user_email='%s'" % user_email)
    if len(result) == 1:
        user_id = result[0][0]
    else:
        insert_to_db("insert into tbl_user(user_email) values('%s')" % user_email)
        user_id = query_db("select user_id from tbl_user where user_email='%s'" % user_email)[0][0]
    return user_id


def get_user_email_by_user_id(user_id):
    return query_db("select user_email from tbl_user where user_id = %s" % user_id)[0][0]


def get_sale_details_by_sale_id(sale_id):
    sale_details = query_db("select sale_name, sale_date from tbl_sale where sale_id=%s" % sale_id)
    return sale_details[0]


def get_device_details_by_device_id(device_id):
    device_details = query_db("select device_name, device_description, price from tbl_device where device_id=%s" % device_id)
    return device_details[0]


def get_extended_device_details_by_sale_device_id(sale_device_id):
    extended_device_details = query_db("select d.device_name, d.device_description, t.type_name, sd.quantity, d.price from tbl_sale_device sd join tbl_device d on sd.device_id=d.device_id join tbl_type t on d.type_id=t.type_id where sd.sale_device_id = %s" % sale_device_id)
    return extended_device_details[0]


def generate_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')


def get_sale_id_by_sale_device_id(sale_device_id):
    sale_id = query_db("select sale_id from tbl_sale_device where sale_device_id=%s" % sale_device_id)[0][0]


def get_device_name_and_sale_name_by_sale_device_id(sale_device_id):
    (device_name, sale_name) = query_db("select d.device_name, s.sale_name from tbl_device d join tbl_sale_device sd on d.device_id=sd.device_id join tbl_sale s on s.sale_id=sd.sale_id where sale_device_id=%s" % sale_device_id)[0]
    return (device_name, sale_name)


def add_new_admin(admin_name, admin_email, plaintext_password):
    if not is_admin(admin_name):
        try:
            hashed_password = hashpw(plaintext_password.encode('UTF_8'), gensalt()).decode()
            insert_to_db("insert into tbl_admin(admin_name, admin_email, hashed_password) values('%s', '%s', '%s')" % (admin_name, admin_email, hashed_password))
            return True
        except Exception as error:
            debug(traceback.format_exc())
    return False


def check_auth(admin_name, plaintext_password):
    if is_admin(admin_name):
        hashed_password = query_db("select hashed_password from tbl_admin where admin_name='%s'" % admin_name)[0][0]
        if hashpw(plaintext_password.encode('UTF_8'), hashed_password.encode('UTF_8')).decode() == hashed_password:
            return True
    return False


def get_bucket_list(user_email, sale_id):
    user_id = get_user_id_by_user_email(user_email)
    items = query_db("select d.device_name from tbl_device d join tbl_sale_device sd on d.device_id=sd.device_id join tbl_user_sale_device usd on sd.sale_device_id=usd.sale_device_id where sd.sale_id=%s and usd.user_id=%s" % (sale_id, user_id))
    return items


def get_hash_of_project():
    import hashlib, os
    directory = os.path.dirname(os.path.realpath(__file__))
    SHAhash = hashlib.sha1()
    if not os.path.exists (directory):
        return -1
    
    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                filepath = os.path.join(root,names)
                try:
                    f1 = open(filepath, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while 1:
	            # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf : break
                    SHAhash.update(hashlib.sha1(buf).hexdigest())
                f1.close()

    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2

    return SHAhash.hexdigest()


def debug(message):
    if app.config['DEBUG'] == True:
        sys.stderr.write("%s - DEBUG: %s\n" % (datetime.now(), message))
        sys.stderr.flush()
