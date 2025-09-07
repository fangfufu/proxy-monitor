# Proxy Speed Monitor

This script monitors the speed and availability of a proxy server by attempting to connect to a list of websites through it. It logs the results to a CSV file and can send email alerts if a connection fails.

## Configuration

The application is configured using a YAML file, by default `config.yaml`. An example configuration file is provided as `example_config.yaml`.

### `proxy`

This section contains the details of the proxy server to be monitored.

- `host`: (Required) The hostname or IP address of your proxy server.
- `port`: (Required) The port number of your proxy server.

**Example:**
```yaml
proxy:
  host: 192.168.1.100
  port: 8080
```

### `monitoring`

This section defines the monitoring parameters.

- `websites`: (Required) A list of websites to use for checking the proxy. The script will iterate through this list and attempt to connect to each one.
- `log_file`: (Required) The path to the CSV file where the monitoring logs will be stored.

**Example:**
```yaml
monitoring:
  websites:
    - https://www.google.com
    - https://www.github.com
  log_file: /var/log/proxy_monitor.log
```

### `email_alerts`

This section is optional and configures email notifications for when the proxy is down.

- `use_local_mta`: (Optional) Set to `true` if you have a configured Mail Transfer Agent (MTA) like `sendmail` or `postfix` on your system. If this is `true`, the other `smtp_*` settings will be ignored. Defaults to `false`.
- `recipient_email`: (Required for email alerts) The email address to which alert emails will be sent.
- `smtp_server`: (Required if `use_local_mta` is `false`) The hostname or IP address of your SMTP server.
- `smtp_port`: (Required if `use_local_mta` is `false`) The port number for the SMTP server (e.g., 587 for TLS, 465 for SSL).
- `smtp_user`: (Required if `use_local_mta` is `false`) The username for authenticating with the SMTP server.
- `smtp_password`: (Required if `use_local_mta` is `false`) The password for authenticating with the SMTP server.

**Example (using an external SMTP server):**
```yaml
email_alerts:
  use_local_mta: false
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
```

## Usage

1.  Rename `example_config.yaml` to `config.yaml` and edit it with your specific details.
2.  Run the script from your terminal, pointing it to your configuration file:

    ```bash
    python3 main.py --config-file config.yaml
    ```

The script also supports overriding configuration options via command-line arguments. For more information, run:
```bash
python3 main.py --help
```
