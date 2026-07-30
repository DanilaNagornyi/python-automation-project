# Website Monitoring and Recovery 🐍

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Gmail](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)

This capstone project from the **Automation with Python** module monitors a
Dockerized web application running on a cloud server and performs automatic
recovery when the application becomes unavailable.

The original demo used Linode. I adapted the project to **DigitalOcean** because
I could not complete Linode's account verification. The monitoring and recovery
workflow remains the same, while the server reboot request uses the DigitalOcean
REST API.

## How it works

The [`monitor-website.py`](monitor-website.py) script:

1. Sends an HTTP request to the application every five minutes.
2. Treats HTTP `200` as a successful health check.
3. Sends an email alert through Gmail SMTP when the application is down.
4. Uses Paramiko and SSH to restart the Docker container when the server is
   reachable but the application returns an error.
5. If the server is unreachable, requests a droplet reboot through the
   DigitalOcean API, waits for SSH to become available, and restarts the
   container.

## Project flow

```text
Scheduled HTTP check
        |
        +-- HTTP 200 ----------------------> Application is healthy
        |
        +-- HTTP error --> Email alert ----> Restart Docker container over SSH
        |
        +-- No connection -> Email alert --> Reboot DigitalOcean droplet
                                             -> Restart container over SSH
```

## Prerequisites

- Python 3
- A DigitalOcean droplet with Docker installed
- A running Docker container that exposes the web application
- SSH access to the droplet
- A Gmail account with an app password
- A DigitalOcean API token with permission to reboot the droplet

## Configuration

Install the Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Use [`.env.example`](.env.example) as a list of the required environment
variables and export them in your shell. For example:

```bash
export EMAIL_ADDRESS="your-email@gmail.com"
export EMAIL_PASSWORD="your-gmail-app-password"
export DIGITAL_OCEAN_TOKEN="your-digitalocean-api-token"
export DIGITAL_OCEAN_DROPLET_ID="your-droplet-id"
export SERVER_IP="your-droplet-public-ip"
export SSH_KEY_PATH="/absolute/path/to/your/private-key"
export CONTAINER_NAME_OR_ID="your-container-name-or-id"
```

Credentials and private keys are not stored in this repository.

## Run the monitor

```bash
python3 monitor-website.py
```

The first health check runs immediately. Further checks run every five minutes,
or at the interval configured through `MONITOR_INTERVAL_MINUTES`.

## Other module exercises

This repository also contains the Python automation exercises completed during
the module: EC2 and EKS status checks, VPC creation, EC2 tagging, EBS snapshot
backup and cleanup, and volume restoration. These scripts use Boto3 and AWS.

---

*Created as part of the TechWorld with Nana DevOps Bootcamp.*
