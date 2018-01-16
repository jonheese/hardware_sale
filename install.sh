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
cp sysconfig/hardware_sale_runner /etc/sysconfig/

echo "Copying service file to systemd directory..."
cp systemd/hardware-sale-runner.service /usr/lib/systemd/system/

echo "Making log directory..."
mkdir /var/log/hardware_sale

echo "Reloading systemd files..."
systemctl daemon-reload

echo "Starting hardware-sale-runner service..."
systemctl start hardware-sale-runner

echo -n "Do you want to auto-start the hardware-sale-runner service? [y/N]: "
read autostart

[ "$autostart" == "y" -o "$autostart" == "Y" ] && systemctl enable hardware-sale-runner

