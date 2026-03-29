import os
import time
import smtplib
import requests
import paramiko
import schedule

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DIGITAL_OCEAN_TOKEN = os.environ.get("DIGITAL_OCEAN_TOKEN")

DIGITAL_OCEAN_DROPLET_ID = os.environ.get("DIGITAL_OCEAN_DROPLET_ID")

SERVER_IP = "146.190.85.128"
APP_URL = f"http://{SERVER_IP}:8080/"
SSH_USERNAME = "root"
SSH_KEY_PATH = "/Users/danielnagorniy/.ssh/id_rsa"
CONTAINER_ID = "024710bb137c"


def restart_server_and_container():
    print("Rebooting the DigitalOcean server...")

    if not DIGITAL_OCEAN_TOKEN:
        raise ValueError("DIGITAL_OCEAN_TOKEN is not set")

    if not DIGITAL_OCEAN_DROPLET_ID:
        raise ValueError("DIGITAL_OCEAN_DROPLET_ID is not set")

    url = f"https://api.digitalocean.com/v2/droplets/{DIGITAL_OCEAN_DROPLET_ID}/actions"
    headers = {
        "Authorization": f"Bearer {DIGITAL_OCEAN_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": "reboot"
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code not in (201, 202):
        raise Exception(
            f"Failed to reboot droplet. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

    print("Reboot request sent successfully. Waiting for server to come back...")

    while True:
        try:
            response = requests.get(APP_URL, timeout=10)
            print(f"Server responded with status {response.status_code}")
            time.sleep(5)
            restart_container()
            break
        except Exception:
            print("Server still unavailable, waiting 10 seconds...")
            time.sleep(10)


def send_notification(email_msg):
    print("Sending an email...")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        message = f"Subject: SITE DOWN\n\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)


def restart_container():
    print("Restarting the application...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=SERVER_IP,
        username=SSH_USERNAME,
        key_filename=SSH_KEY_PATH,
        timeout=20,
    )

    stdin, stdout, stderr = ssh.exec_command(f"docker start {CONTAINER_ID}")

    out = stdout.read().decode()
    err = stderr.read().decode()

    if out:
        print("STDOUT:", out)
    if err:
        print("STDERR:", err)

    ssh.close()
    print("Application is restarted")


def monitor_application():
    try:
        response = requests.get(APP_URL, timeout=10)

        if response.status_code == 200:
            print("Application is running successfully")
        else:
            print("Application is not running")
            msg = f"Application returned {response.status_code}. Fix the issue!"
            send_notification(msg)
            restart_container()

    except Exception as ex:
        print(f"Connection error happened: {ex}")
        msg = "Application is not accessible at all"
        send_notification(msg)
        restart_server_and_container()


schedule.every(5).minutes.do(monitor_application)

while True:
    schedule.run_pending()
    time.sleep(1)