#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
from flask import render_template
from time import sleep
from datetime import datetime, timedelta
from random import randint
import signal
from common import debug, app, query_db, get_sale_name_by_sale_id, get_sale_details_by_sale_id, \
                   get_user_email_by_user_id, get_device_details_by_device_id, send_email, update_db, \
                   deactivate_sale


def run_sale(sale_id):
    try:
        debug("Running sale %s, %s" % (get_sale_name_by_sale_id(sale_id), sale_id))
        devices = query_db("select distinct device_id from view_entrants where sale_id=%s" % sale_id)
        for device in devices:
            device_id = device[0]
            debug("  Selecting buyers for device %s" % device_id)
            entrants = list(query_db("select user_id from tbl_user_sale_device usd join tbl_sale_device sd on sd.sale_device_id=usd.sale_device_id where sd.sale_id=%s and device_id=%s order by user_id" % (sale_id, device_id)))
            (sale_device_id, quantity) = query_db("select sale_device_id, quantity from tbl_sale_device where sale_id=%s and device_id=%s" % (sale_id, device_id))[0]

            debug("    %s of these devices on hand" % quantity)
            debug("    %s buyers want one" % len(entrants))
            chosen_buyers = []
            # Check if there are more names in the bucket than devices on hand
            if len(entrants) > quantity:
                debug("     We need to go to a random selection process")
                # Loop until we've selected buyers for all of the available items or we've exhausted all of the entrants (which should never happen, but whatever)
                while len(chosen_buyers) < quantity and len(entrants) > 0:
                    # Choose a random integer from 0 to the highest index in the list
                    chosen_buyer_index = randint(0, len(entrants)-1)
                    # Pop the random buyer out of 'entrants' and append him to the 'chosen_buyers' list
                    chosen_buyers.append(entrants.pop(chosen_buyer_index))
                # Give the unselected buyers the bad news
                notify_buyers(False, entrants, sale_id, device_id, sale_device_id)
            else:
                # Don't bother picking names out of the hat if there are more (or the same number of) devices on hand than names
                debug("      We don't need to go to a random selection process")
                chosen_buyers = entrants
            # Give the selected entrants the good news
            notify_buyers(True, chosen_buyers, sale_id, device_id, sale_device_id)
            deactivate_sale(sale_id)
    except Exception as error:
        debug(traceback.format_exc())


def notify_buyers(success, buyers, sale_id, device_id, sale_device_id):
    for buyer in buyers:
        user_id = buyer[0]
        debug("      Notifying buyer %s, success: %s" % (user_id, success))
        (sale_name, sale_date) = get_sale_details_by_sale_id(sale_id)
        (device_name, device_description, price) = get_device_details_by_device_id(device_id)
        user_email = get_user_email_by_user_id(user_id)
        if success:
            close_date = sale_date.replace(hour=17,minute=00) + timedelta(hours=24)
            send_email(render_template('notify_success_buyer.html', sale_name=sale_name, sale_date=sale_date, device_name=device_name, device_description=device_description, price=price, close_date=close_date), user_email, 'Success!')
            update_db("update tbl_user_sale_device set won=1 where user_id=%s and sale_device_id=%s" % (user_id, sale_device_id))
        else:
            send_email(render_template('notify_failed_buyer.html', sale_name=sale_name, sale_date=sale_date, device_name=device_name, device_description=device_description, price=price), user_email, 'Sorry :(')


def signal_handler(signal, frame):
    debug("Hardware Sale salerunner exiting on SIGINT...")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) > 1:
        logfile = sys.argv[1]
        sys.stderr = open(logfile, 'a')
    debug("Hardware Sale salerunner starting...")
    interval = app.config['SALE_RUNNER_INTERVAL']
    with app.app_context():
        while True:
            current_time = datetime.now()
            # Calculate the number of seconds to the nearest N minute multiple, N = sale_runner_interval
            sleep_seconds = (60 - current_time.second) + (60 * ((interval - (current_time.minute % interval)) - 1))
            target_time = current_time + timedelta(0, sleep_seconds)
            debug("Sleeping for %s seconds to reach %s-minute interval of %s" % (sleep_seconds, interval, target_time.time()))
            sleep(sleep_seconds)

            active_sales = query_db("select sale_id from tbl_sale where active=1 and sale_date<=now()")
            for sale in active_sales:
		debug("Running sale: %s" % sale)
                run_sale(sale[0])
