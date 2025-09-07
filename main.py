import requests
import time
import smtplib
import argparse
import yaml  # Using PyYAML for config parsing
import os
import socket
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd

def check_proxy_speed(url, proxy):
    """
    Checks the time it takes to download a web page through a proxy.

    Args:
        url (str): The URL of the web page to visit.
        proxy (dict): A dictionary containing the proxy information.

    Returns:
        float: The time taken to download the page in seconds, or None if an error occurs.
    """
    try:
        start_time = time.time()
        response = requests.get(url, proxies=proxy, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url} via proxy: {e}")
        return None

def sanitize_sheet_name(url):
    """Sanitizes a URL to be a valid Excel sheet name."""
    name = url.replace("https://", "").replace("http://", "").replace("www.", "")
    invalid_chars = r'[]/\?*:'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name[:31]

def log_to_excel(log_file, url, download_time, status):
    """
    Logs the monitoring result to an Excel file, with one sheet per website.

    Args:
        log_file (str): The path to the Excel log file.
        url (str): The URL that was checked.
        download_time (float): The download time in seconds. Can be 0 if status is 'DOWN'.
        status (str): 'UP' or 'DOWN'.
    """
    sheet_name = sanitize_sheet_name(url)
    df_new_row = pd.DataFrame([[datetime.now().isoformat(), url, f"{download_time:.4f}", status]],
                              columns=['Timestamp', 'URL', 'Download Time (s)', 'Status'])

    try:
        if os.path.exists(log_file):
            with pd.ExcelFile(log_file) as xls:
                sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        else:
            sheets = {}

        if sheet_name in sheets:
            sheets[sheet_name] = pd.concat([sheets[sheet_name], df_new_row], ignore_index=True)
        else:
            sheets[sheet_name] = df_new_row

        with pd.ExcelWriter(log_file, engine='openpyxl') as writer:
            for sheet, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet, index=False)

    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")


def send_email_alert(args, subject, body):
    """
    Sends an email alert using either a local MTA or an external SMTP server.

    Args:
        args (Namespace): The parsed command-line/config arguments.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    if not args.recipient_email:
        print("Recipient email not configured. Skipping email alert.")
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['To'] = args.recipient_email
    
    try:
        if args.use_local_mta:
            # For local MTA, construct a generic 'From' address.
            user = os.environ.get('USER') or 'proxy-monitor'
            hostname = socket.gethostname()
            msg['From'] = f"{user}@{hostname}"
            with smtplib.SMTP('localhost') as server:
                server.send_message(msg)
            print("Email alert sent successfully via local MTA.")
        else:
            # Use external SMTP server with authentication
            if not all([args.smtp_server, args.smtp_port, args.smtp_user, args.smtp_password]):
                print("External SMTP server configuration is not complete. Skipping email alert.")
                return
            msg['From'] = args.smtp_user
            with smtplib.SMTP_SSL(args.smtp_server, args.smtp_port) as server:
                server.login(args.smtp_user, args.smtp_password)
                server.send_message(msg)
            print("Email alert sent successfully via external SMTP.")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

def main():
    """Main function to run the proxy monitor."""
    
    conf_parser = argparse.ArgumentParser(
        description="Monitor proxy server speed and availability.",
        add_help=False 
    )
    conf_parser.add_argument('--config-file', help="Path to the configuration file.", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    if args.config_file:
        try:
            with open(args.config_file, 'r') as f:
                config = yaml.safe_load(f)
            if config:
                # Flatten the config for argparse defaults
                if 'proxy' in config and config['proxy']:
                    defaults.update(config['proxy'])
                if 'monitoring' in config and config['monitoring']:
                    defaults.update(config['monitoring'])
                if 'email_alerts' in config and config['email_alerts']:
                    defaults.update(config['email_alerts'])
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"Error reading or parsing config file {args.config_file}: {e}")

    parser = argparse.ArgumentParser(
        description="Monitor proxy server speed and availability.",
        parents=[conf_parser]
    )
    parser.set_defaults(**defaults)

    parser.add_argument('--proxy-host', dest='host', help="Proxy server host or IP address.")
    parser.add_argument('--proxy-port', dest='port', type=int, help="Proxy server port.")
    parser.add_argument('--websites', nargs='+', help="List of websites to check.")
    parser.add_argument('--log-file', help="Path to the Excel log file.")
    
    email_group = parser.add_argument_group('Email Alert Options')
    email_group.add_argument('--alert-email', dest='recipient_email', help="Email address to send alerts to.")
    email_group.add_argument('--use-local-mta', action='store_true', default=defaults.get('use_local_mta', False), help="Use the system's local MTA (e.g., sendmail) for alerts.")
    email_group.add_argument('--smtp-server', help="SMTP server for email alerts (if not using local MTA).")
    email_group.add_argument('--smtp-port', type=int, help="SMTP port for email alerts (if not using local MTA).")
    email_group.add_argument('--smtp-user', help="SMTP username for email alerts.")
    email_group.add_argument('--smtp-password', help="SMTP password for email alerts.")
    
    args = parser.parse_args(remaining_argv)

    if not all([args.host, args.port, args.websites, args.log_file]):
        parser.error("Missing required arguments. Please provide them via command line or a config file: --proxy-host, --proxy-port, --websites, --log-file")

    proxy_url = f"http://{args.host}:{args.port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    for website in args.websites:
        print(f"Checking {website} through proxy {args.host}...")
        download_time = check_proxy_speed(website, proxies)

        if download_time is not None:
            print(f"Successfully connected to {website}. Download time: {download_time:.4f} seconds.")
            log_to_excel(args.log_file, website, download_time, 'UP')
        else:
            print(f"Failed to connect to {website} through the proxy.")
            log_to_excel(args.log_file, website, 0, 'DOWN')
            subject = "Proxy Server Down Alert!"
            body = f"The proxy server at {args.host}:{args.port} seems to be down.\n" \
                   f"Failed to connect to {website} at {datetime.now().isoformat()}.\n" \
                   f"Please check the proxy server status."
            send_email_alert(args, subject, body)

if __name__ == "__main__":
    main()

