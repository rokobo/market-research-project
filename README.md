# Market research project

- [Market research project](#market-research-project)
  - [Excel workbook](#excel-workbook)
  - [AWS costs and free tier](#aws-costs-and-free-tier)
  - [Clientside callbacks and authentication](#clientside-callbacks-and-authentication)
  - [Environment file](#environment-file)
  - [Minify assets](#minify-assets)
  - [AWS deployment to EC2](#aws-deployment-to-ec2)
    - [Launch instance and get key pair credential](#launch-instance-and-get-key-pair-credential)
    - [Configure network settings](#configure-network-settings)
    - [Set up application server](#set-up-application-server)
    - [Set up Nginx](#set-up-nginx)
    - [Changing code, re-deploying and aliases](#changing-code-re-deploying-and-aliases)


To the next developer that takes over this project, here are some important considerations and guidelines to ensure a smooth setup and maintenance of the infrastructure. This project requires careful attention to detail during the initial setup phase, as well as ongoing management to keep everything running smoothly.

In the following sections, you will find detailed instructions on how to properly configure the environment, set up necessary dependencies, and manage the infrastructure effectively. Following these guidelines will help you avoid common pitfalls and ensure that the project remains stable and maintainable. However, **DO NOT** follow this guide blindly and always study what every configuration and instruction is doing.

Variables that you will need to set up will be indicated by: `<var1>`.

## Excel workbook

The `aggregate_reports()` function is responsible for creating the Excel workbook using the `.csv` files from the reports. In case you ever need to change anything, be aware of the following:

1. The goal of the sheets is to be as connected as possible, the main sheet is the `Coleta_Mes` sheet and will sometimes suffer manual corrections. The other sheets should never need any manual change, since the changes must be propagated to them via formulas.
2. To create the workbook, `XlsxWriter` is being used. It has some behaviors that you need to pay attention to:
   1. The dynamic array formulas must be created with `worksheet.write_dynamic_array_formula()`.
   2. The spill range operator, like `A2#`, must be referenced with `ANCHORARRAY(A2)`.
   3. `pd.ExcelWriter` must be passed engine kwargs to prevent newer functions not being interpreted correctly.
   4. Sometimes the formulas end up being interpreted as implicit intersection, you can use `SINGLE()` to prevent this behavior.

## AWS costs and free tier

This project relies heavily on the free tier of EC2 with EBS and Lambda. EC2 has 12 months free tier, which is a yearly maintenance for the project developer. Just create a new account and use the free tier again.

That said, the only cost that this project is supposed to possibly have is if the data sent out of the server is bigger than the free tier limit (always check if there were any changes to the billing policy). Ways to decrease or eliminate this cost are explained in the following sections.

## Clientside callbacks and authentication

To prevent possibly having a large AWS bill, the data being sent out of EC2 must be minimized. To achieve this:

1. Clientside callbacks were used because they do not send or receive data from the EC2 server. Some functions still had to be server callbacks because they either need to send data or need to create components dynamically (although I imagine it is possible to do this through clientside callbacks).
2. `dash_auth` was used to prevent page load and minimize data sent out from the server to people who are not involved in the project. Considerations about the user/password duo is explained in the next section.
3. One common mistake when creating callbacks in dash is not understanding the order in which the callbacks are called. Sometimes they are not even constant. One way to handle this is to use dummy inputs and outputs. If only one function outputs to a dummy container, then you can use as an input for a callback you want executed later.

## Environment file

If you see in the `main.py` script, I made calls `getenv()`. This function is using a `.env` file in my directory to load certain variables. This file must **NEVER** be publicly available. In case it ever is, change all passwords and authentication tokens immediately. This file must be passed configured manually and not via GitHub.

## Minify assets

In order to decrease outgoing data from the application server, minifying the assets can decrease the data sent from the server to the user. Both CSS and Javascript files can be minified before setting up the web server. However, this is not strictly necessary, since the assets will be compressed by the Nginx server. Minifying will help decrease the size a little, although compression seems to be enough.

It is worth noting that partially minifying the assets is a good alternative. Simply avoid spaces and newlines when possible. Personally, I remove spaces and newlines on parts of the code that will not make the code overly cluttered and hard to read.

## AWS deployment to EC2

To deploy to EC2, you will need a AWS account (not the same as amazon account) that will be renewed every 12 months to keep the free tier benefits. The following steps should provided a general guideline on how to set it up.

### Launch instance and get key pair credential

One of the first things that can be specified in the EC2 configuration is the instance type of the EC2 service. Each instance type will give you a virtual machine with different hardware configurations. Look for the best instance type that has `Free tier eligible` specified:

<center><img src="images/launch.png?raw=true" alt="." width="60%"/></center>

Then configure your key pair file for accessing your EC2 instance with SSH. While RSA is acceptable, ED25519 should be safer. This file must **NEVER** be publicly available.:

<center><img src="images/keypair.png?raw=true" alt="." width="60%"/></center>

### Configure network settings

After launching the instance, it can then be customized to have additional storage. To do this, configure the EC2 instance to use EBS storage, which is free-tier eligible for up to 30GB.

Then, enable security groups, which act as virtual firewalls for your EC2 instances to control incoming and outgoing traffic. When you launch an instance, you can assign it one or more security groups. Each instance in your VPC (Virtual Private Cloud) is associated with one or more security groups, and each security group can have rules that allow traffic to or from its associated instances.

Security groups are important because they can prevent DDoS attacks and potentially decrease the outgoing data from the instance, which will save money. Configure your security groups to allow connections from:

+ SSH (port 22)
+ HTTP (port 80)
+ HTTPS (port 443)

After this step, launch the instance.

### Set up application server

To get the web server up and running, you will need to connect to the EC2 instance. This can be done via the browser-based client or a terminal using SSH (you will need your `.pem` key to do this):

```sh
ssh -i "<key-pair-name.pem>" <ec2-user>@<your-ec2-ip>
```

Check if SSH response that is printed on your terminal matches the fingerprint of your instance. You will need to go to the web console and check the system logs to find the fingerprint and check if they are the same. **DO NOT** continue if the fingerprints do not match. Here is an example response:

```
The authenticity of host 'ec2-198-51-100-1.us-east-2.compute.amazonaws.com (198-51-100-1)' can't be established.
ECDSA key fingerprint is l4UB/neBad9tvkgJf1QZWxheQmR59WgrgzEimCG6kZY.
Are you sure you want to continue connecting (yes/no)?
```

However, for simplicity, using instance connect from the web console is simpler and I recommend it.

<center><img src="images/connect.png?raw=true" alt="." width="60%"/></center>

Update system packages and install dependencies:

```sh
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python3.12 python3-pip python3.12-venv nginx
```

Clone your application, set up virtual environment and install python dependencies:

```sh
git clone <https://github.com/your-repo/your-project.git>
cd <your-project>
python3.12 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Set up environment variables via the `.env` file. The `SECRET_KEY` is just a string that is used for security-related operations of the Flask server that the app uses (for our case, it is used for saving the application status for each user as local cookies) and the `APP_USERNAME`/`APP_PASSWORD` are the credentials that users must type on the application to get access to the content of the page:

```sh
echo "SECRET_KEY=<your_secret_key>" >> .env
echo "APP_USERNAME=<your_username>" >> .env
echo "APP_PASSWORD=<your_password>" >> .env
```

Before starting the application, check if the localhost port that is used by the application is in use somewhere. Run the following command and ensure it says failed to connect:

```sh
curl 127.0.0.1:<application-port>
```

Start your application WSGI server as a daemon (run in background):

```sh
gunicorn src.main:server --daemon -b 127.0.0.1:<application-port>
```

If Gunicorn is not found, use `which gunicorn` to get the path from the virtual environment's Gunicorn, the use the full path instead:

```sh
<path-to-gunicorn> src.main:server --daemon -b 127.0.0.1:<application-port>
```

### Set up Nginx

Navigate to Nginx sites configuration file:

```sh
sudo nano /etc/nginx/sites-available/<your-ec2-ip>
```

Type the following into the file to configure the reverse proxy:

```nginx
server {
   listen 80;
   listen [::]:80;
   server_name <your-ec2-ip>;

   location / {
      proxy_pass http://127.0.0.1:<application-port>;
      include proxy_params;
   }
}
```

Then create a symbolic link with the enabled sites file:

```sh
sudo ln -s /etc/nginx/sites-available/<your-ec2-ip> /etc/nginx/sites-enabled/
```

Navigate to Nginx main configuration file:

```sh
sudo nano /etc/nginx/nginx.conf
```

Ensure the following lines are in the file (uncomment or add) to enable asset compression:

```nginx
  gzip on;
  gzip_disable "msie6";
  gzip_vary on;
  gzip_proxied any;
  gzip_comp_level 6;
  gzip_buffers 16 8k;
  gzip_http_version 1.1;
  gzip_min_length 256;
  gzip_types
    application/atom+xml
    application/geo+json
    application/javascript
    application/x-javascript
    application/json
    application/ld+json
    application/manifest+json
    application/rdf+xml
    application/rss+xml
    application/xhtml+xml
    application/xml
    font/eot
    font/otf
    font/ttf
    image/svg+xml
    text/css
    text/javascript
    text/plain
    text/xml;
```

Restart Nginx server and check status of the server:

```sh
sudo systemctl restart nginx
sudo systemctl status nginx
```

### Changing code, re-deploying and aliases

Changing the web app code will be frequent as new functionalities are built. To simplify this process, aliases can be created so that you don't have to type long commands in the AWS console. The aliases can be done as follows:

```sh
alias s1="sudo killall gunicorn"
alias s2="source .venv/bin/activate"
alias s3="git pull origin main"
alias s4="gunicorn src.main:server --daemon -b 127.0.0.1:8060"
```

So to change the server to the newest version, you simply need to kill all Gunicorn processes, active the virtual environment, update code by pulling the newest version from GitHub and restarting Gunicorn:

```sh
s1
s2
s3
s4
```
