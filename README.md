# Proxy Monitor

This script monitors the speed and availability of a proxy server by attempting to connect to a list of websites through it. It logs the results to an Excel file and can send email alerts if a connection fails.

## Features

*   **Proxy Monitoring**: Checks proxy server health by connecting to specified websites.
*   **Performance Logging**: Logs connection status (UP/DOWN) and download times to an Excel file. Each monitored website has its own sheet in the Excel file.
*   **Email Alerts**: Sends email notifications if the proxy server appears to be down.
    *   Supports sending emails via an external SMTP server.
    *   Supports sending emails via a local Mail Transfer Agent (MTA) like `sendmail` or `postfix`.
*   **Flexible Configuration**: Configure the application with a YAML file or override settings with command-line arguments.

## Requirements

*   Python 3.6+
*   The following Python libraries:
    *   `requests`
    *   `PyYAML`
    *   `pandas`
    *   `openpyxl`

You can install these with:
```bash
pip install requests PyYAML pandas openpyxl
```

## Configuration

The application is configured using a YAML file. You can rename `example_config.yaml` to `config.yaml` and edit it to your needs.

### `proxy`

This section contains the details of the proxy server to be monitored.

*   `host`: (Required) The hostname or IP address of your proxy server.
*   `port`: (Required) The port number of your proxy server.

**Example:**
```yaml
proxy:
  host: 192.168.1.100
  port: 8080
```

### `monitoring`

This section defines the monitoring parameters.

*   `websites`: (Required) A list of websites to use for checking the proxy.
*   `log_file`: (Required) The path to the Excel file where the monitoring logs will be stored.

**Example:**
```yaml
monitoring:
  websites:
    - https://www.google.com
    - https://www.github.com
  log_file: /var/log/proxy_monitor.xlsx
```

### `email_alerts`

This section is optional and configures email notifications for when the proxy is down.

*   `recipient_email`: (Required for email alerts) The email address to which alert emails will be sent.
*   `use_local_mta`: (Optional) Set to `true` to use a local MTA (e.g., `sendmail`). Defaults to `false`.
*   `sendmail_path`: (Optional) The path to the `sendmail` executable. If not provided, the script will try to use `sendmail` from the system's PATH.
*   `smtp_server`: (Required if `use_local_mta` is `false`) The hostname or IP address of your SMTP server.
*   `smtp_port`: (Required if `use_local_mta` is `false`) The port number for the SMTP server.
*   `smtp_user`: (Required if `use_local_mta` is `false`) The username for authenticating with the SMTP server.
*   `smtp_password`: (Required if `use_local_mta` is `false`) The password for authenticating with the SMTP server.

**Example (using an external SMTP server):**
```yaml
email_alerts:
  recipient_email: your_email@example.com
  smtp_server: smtp.example.com
  smtp_port: 587
  smtp_user: your_email@example.com
  smtp_password: your_password
```

**Example (using a local MTA):**
```yaml
email_alerts:
  use_local_mta: true
  recipient_email: your_email@example.com
  sendmail_path: /usr/sbin/sendmail
```

## Usage

1.  Install the required libraries (see Requirements section).
2.  Rename `example_config.yaml` to `config.yaml` and edit it with your specific details.
3.  Run the script from your terminal:
    ```bash
    python3 main.py --config-file config.yaml
    ```

## Command-line Arguments

You can override the settings from the configuration file using command-line arguments.

*   `--config-file FILE`: Path to the configuration file.
*   `--proxy-host HOST`: Proxy server host or IP address.
*   `--proxy-port PORT`: Proxy server port.
*   `--websites URL1 URL2 ...`: List of websites to check.
*   `--log-file FILE`: Path to the Excel log file.

### Email Alert Options

*   `--alert-email EMAIL`: Email address to send alerts to.
*   `--use-local-mta`: Use the system's local MTA for alerts.
*   `--sendmail-path PATH`: Path to the sendmail executable.
*   `--smtp-server SERVER`: SMTP server for email alerts.
*   `--smtp-port PORT`: SMTP port for email alerts.
*   `--smtp-user USER`: SMTP username for email alerts.
*   `--smtp-password PASSWORD`: SMTP password for email alerts.

For more information, run:
```bash
python3 main.py --help
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
