#!/bin/bash

echo "Installing EPEL yum repo..."
yum install -y epel-release

echo "Installing yum package prerequisites..."
yum install httpd mod_ssl mod_wsgi python-pip git python-devel mysql-devel make gcc openssl-devel -y

echo "Updating pip..."
pip install --upgrade pip

echo "Installing pip package prerequisites..."
pip install flask bcrypt mysqlclient

echo "Installing hardware_sale_runner service..."
echo "Copying base sysconfig file..."
sed -i 's/hardware_sale/hardware_sale_test/g' sysconfig/hardware_sale_runner
cp sysconfig/hardware_sale_runner /etc/sysconfig/hardware_sale_runner-test
sed -i 's/hardware_sale_test/hardware_sale/g' sysconfig/hardware_sale_runner

echo "Copying service file to systemd directory..."
sed -i 's/hardware_sale_runner/hardware_sale_runner-test/g' systemd/hardware-sale-runner.service
cp systemd/hardware-sale-runner.service /usr/lib/systemd/system/hardware-sale-runner-test.service
sed -i 's/hardware_sale_runner-test/hardware_sale_runner/g' systemd/hardware-sale-runner.service

echo "Making log directory..."
mkdir /var/log/hardware_sale_test

echo "Reloading systemd files..."
systemctl daemon-reload

echo "Starting hardware-sale-runner service..."
systemctl start hardware-sale-runner-test

echo -n "Do you want to auto-start the hardware-sale-runner service? [y/N]: "
read autostart

[ "$autostart" == "y" -o "$autostart" == "Y" ] && systemctl enable hardware-sale-runner-test
