## Flexential Hardware Sale app

This app runs the Flexential Hardware Sale.  It has two major components:

 - hardware_sale.py - WSGI webapp for processing user and admin requests (the web GUI)
 - salerunner.py - Python app that runs in the background waiting for a sale to expire, at which point it does all of the things necessary to make the sale a reality (the daemon)

The web GUI is designed to be run as a WSGI app in Apache or nginx+gunicorn, and the daemon is designed to be run as a systemd service.

### Installation:
#### Prerequisites ####
 - There are a number of prerequisite packages that you will need in order to run the Hardware Sale app:
   - yum packages:
     - epel-release
     - httpd
     - mod_ssl
     - mod_wsgi
     - git
     - make
     - gcc
     - mysql-devel
     - openssl-devel
     - python-devel
     - python-pip
  - pip packages:
     - flask
     - bcrypt
     - mysqlclient

  - You can use the `install.sh` (or `install-test.sh`) script to handle the installation of these prerequisites, or you can install them yourself manually -- the script is recommended.

#### The web GUI:
 - Create your WSGI file, replacing /path/to/webapp with the directory where you cloned the project:

    ```
    cp hardware_sale-dist.wsgi hardware_sale.wsgi
    vi hardware_sale.wsgi
    ```
 - Install Apache, download all of the files in this project to a local dir, then point Apache to your `hardware_sale.wsgi`.
 
    eg.
    ```
    WSGIDaemonProcess hardware_sale user=apache group=apache threads=5 python-path=/var/www/

    WSGIScriptAlias / /var/www/hardware_sale/hardware_sale.wsgi
    <Directory /var/www/hardware_sale>
           WSGIProcessGroup hardware_sale
           WSGIApplicationGroup %{GLOBAL}
           Order deny,allow
           Allow from all
    </Directory>
    ```
 - Start the apache service

    ```
    systemctl start httpd
    ```
 - The web GUI should be available wherever you configured Apache to put the WSGI app.

#### The daemon:
 - The `install.sh` (or `install-test.sh`) script handles the installation of the daemon service, so it's highly recommended that you use that.  Alternatively, the manual steps are below.

 - Put the config file in place

    ```
    cp sysconfig/hardware_sale_runner /etc/sysconfig/
    ```
 - Install the systemd service

    ```
    cp systemd/hardware-sale-runner.service /usr/lib/systemd/system/
    ```
 - Reload the service files from disk

    ```
    systemctl daemon-reload
    ```
 - Start the daemon

    ```
    systemctl start hardware-sale-runner
    ```
 - Optional: Enable autostart on boot

    ```
    systemctl enable hardware-sale-runner
    ```
 - NOTE: Logs are placed in `/var/log/hardware_sale/salerunner.log` by default.
