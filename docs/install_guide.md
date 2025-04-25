# Software Installation Guide: 6th Street Pizza Store

## Introduction

The 6th Street Pizza Store website is a Django application which allows users customers to order pizza online and track their orders.

Users of the application will not need to install anything as it is a website.
This guide is intended for system administrators to deploy the application.

## System Requirements

The application is designed to run on a Ubuntu 22.04 Linux server. For this guide, it is assumed the system administrator has already provisioned a Ubuntu 22.04 server with a root user account setup.

The following hardware/network requirements should be satisfied:

- \> 4GB Memory
- \> 50GB SSD Storage
- \> 1Gbps Symmetric network link
- Dedicated IPv4 Address

The following services must be setup to deploy the application:

- MySQL database
- NginX server

The following third-party services must be setup to deploy the application:

- Stripe Payments
- SMTP Mail Server

Different SMTP hosting providers have varying procedures for setup. This guide assumes you already have a SMTP server available.

## Installing Software

Unless stated, all command line operations assume the system administrator is logged in as root on the Ubuntu 22.04 server.

### Step 1 Prepare server

Update server packages

```shell
$ apt update
$ apt upgrade
```

Install required dependencies

```shell
$ apt install python3-venv python3-dev python3-pip pipenv mysql-server pkg-config  build-essential libmysqlclient-dev nginx curl -y
```

### Step 2 Database setup

Setup MySQL installation

Run install script

```shell
$ mysql_secure_installation
```

Open a MySQL Prompt

```
$ mysql -u root -p
```

In the MySQL Prompt, run the following command

```SQL
CREATE DATABASE pizza CHARACTER SET UTF8;
```

Create a database user (Replace example password with something secure. Write this down)

```SQL
CREATE USER pizza_db_user@localhost IDENTIFIED BY 'S3cure P@ssword';
```

Assign privileges to user

```SQL
GRANT ALL PRIVILEGES ON pizza.* TO pizza_db_user@localhost;
```

Flush changes

```SQL
FLUSH PRIVILEGES;
```

Exit the MySQL Prompt

```SQL
exit
```

### Step 3 Gunicorn

Create SystemD service for Gunicorn.

Create service file

```
$ vim /etc/systemd/system/gunicorn.service
```

Inside the file, paste the following contents

```toml
[Unit]
Description=Gunicorn daemon for 6th Street Pizza Django app
After=network.target

[Service]
User=pizza
Group=pizza
WorkingDirectory=/var/www/pizza
ExecStart=/usr/bin/pipenv run gunicorn --access-logfile - --workers 3 --bind unix:/var/www/pizza/gunicorn.sock myproject.wsgi:application
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Step 4 Nginx

Remove default site

```
$ rm /etc/nginx/sites-enabled/default
```

Create an NginX site file

```
$ vim /etc/nginx/sites-available/pizza
```

Inside the file, paste the following contents

```nginx
server {
    listen 80;
    server_name 6thstreetpizza.store;

    location /static/ {
        root /var/www/pizza/static;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/pizza/gunicorn.sock;
    }
}
```

Enable the site by creating a symlink.

```
$ ln -s /etc/nginx/sites-available/pizza /etc/nginx/sites-enabled
```

Allow Nginx traffic past the firewall

```
$ ufw allow 'Nginx Full'
```

### Step 5 User setup

Create a user to run the software

```
$ useradd -d /home/pizza -m -s/bin/bash pizza
```

### Step 6 Install script

The install script downloads the project from github and deploys the software.

Create the install script

```
$ vim /root/pizza_install.sh
```

Inside the file, paste the following text

```sh
#!/bin/bash
systemctl stop gunicorn
rm -r /var/www/pizza
# Don't clone all of the git history, only the latest revision.
git clone --depth 1 -b Production https://github.com/bjgill33/6th-Street-Pizza /var/www/pizza
cp .env.prod /var/www/pizza/.env.prod
chown -R pizza:pizza /var/www/pizza
sudo -u pizza sh -c "(cd /var/www/pizza;pipenv install)"
# Pipenv doesn't support production only dependencies so this is the hack.
sudo -u pizza sh -c "(cd /var/www/pizza;pipenv install mysqlclient)"
sudo -u pizza sh -c "(cd /var/www/pizza;pipenv run python manage.py migrate)"
systemctl start gunicorn
```

Save the file.

**Do not yet run the install script**

Make the script executable

```
$ chmod +x /root/pizza_install.sh
```

### Step 7 Configuring Env Variables

Inside the root directory, create `.env.prod` to hold the production environmental variables.

```
$ vim /root/.env.prod
```

Inside the file, paste

```
DJANGO_SECRET_KEY="<snip>"
DATABASE_TYPE="MYSQL"
MYSQL_DB_NAME="pizza"
MYSQL_DB_USER="pizza_db_user"
MYSQL_DB_PASSWORD="<snip>"
MYSQL_DB_HOST="127.0.0.1"
MYSQL_DB_PORT="3306"
SEND_GRID_API_KEY="null"
STRIPE_SECRET_KEY="<snip>"
STRIPE_PUBLIC_KEY="<snip>"
EMAIL_HOST = "<snip>"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "noreply@6thstreetpizza.store"
EMAIL_HOST_PASSWORD = "<snip>"
DEFAULT_FROM_EMAIL = "6th Street Pizza <noreply@6thstreetpizza.store>"
```

each field with `<snip>` in it must be replaced with data for full functionality.

#### Django

Fill `DJANGO_SECRET_KEY` with a secure secret key for Django operation

#### MySQL

Fill `MYSQL_DB_PASSWORD` with the password you chose earlier.

#### Stripe

Follow [stripes documentation on API keys](https://docs.stripe.com/keys) and fill
`STRIPE_SECRET_KEY` and `STRIPE_PUBLIC_KEY` with their respective keys

#### Smtp

Obtain the email server address and password from your email server host and put them into `EMAIL_HOST` and `EMAIL_PASSWORD` respectively. You may also need to configure the port and other settings. Follow your email host's documentation.

### Step 8 Run install script

The server should now be ready to run the install script.

Run the install script.

```shell
$ /root/pizza_install.sh
```

### Step 9 load base data

Some base data is required for the menu items. This data is easily loaded.

Run

```shell
$ sudo -u pizza sh -c "(cd /var/www/pizza;pipenv run python mange.py loaddata database_dump.json)"
```

### Step 10 Restart all services

Run

```shell
$ systemctl enable gunicorn
```

```shell
$ systemctl restart nginx
$ systemctl restart gunicorn
```

The server is now setup and the application is now installed.

## Updating software

To update the software, log into the server and run the following command.

```shell
$ ./root/pizza_install.sh
```

The server should automatically redeploy the Django application.

## Troubleshooting

On the server, make sure that nginx and gunicorn aren't throwing any errors

```shell
$ systemctl status nginx
```

```shell
$ systemctl status gunicorn
```

## Uninstalling

To uninstall the software and remove all traces, run the following commands on the server.

Run

```shell
$ apt purge mysql-server libmysqlclient-dev -y
$ systemctl disable gunicorn
$ systemctl stop gunicorn
$ rm /etc/systemd/system/gunicorn.service
$ rm -rf /var/www/pizza
$ rm /root/.env.prod
$ rm /root/pizza_install.sh
$ userdel pizza
$ rm -rf /home/pizza
$ systemctl restart nginx
```
