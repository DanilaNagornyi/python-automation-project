import os
import shlex
import smtplib
import time
from email.message import EmailMessage

import paramiko
import requests
import schedule


EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DIGITAL_OCEAN_TOKEN = os.environ.get("DIGITAL_OCEAN_TOKEN")
DIGITAL_OCEAN_DROPLET_ID = os.environ.get("DIGITAL_OCEAN_DROPLET_ID")

SERVER_IP = os.environ.get("SERVER_IP")
APP_PORT = os.environ.get("APP_PORT", "8080")
APP_URL = os.environ.get("APP_URL") or (
    f"http://{SERVER_IP}:{APP_PORT}/" if SERVER_IP else None
)
SSH_USERNAME = os.environ.get("SSH_USERNAME", "root")
SSH_KEY_PATH = os.environ.get("SSH_KEY_PATH")
CONTAINER_NAME_OR_ID = os.environ.get("CONTAINER_NAME_OR_ID")

MONITOR_INTERVAL_MINUTES = int(os.environ.get("MONITOR_INTERVAL_MINUTES", "5"))
RECOVERY_ATTEMPTS = int(os.environ.get("RECOVERY_ATTEMPTS", "30"))


def validate_configuration():
    required_variables = {
        "EMAIL_ADDRESS": EMAIL_ADDRESS,
        "EMAIL_PASSWORD": EMAIL_PASSWORD,
        "DIGITAL_OCEAN_TOKEN": DIGITAL_OCEAN_TOKEN,
        "DIGITAL_OCEAN_DROPLET_ID": DIGITAL_OCEAN_DROPLET_ID,
        "SERVER_IP": SERVER_IP,
        "SSH_KEY_PATH": SSH_KEY_PATH,
        "CONTAINER_NAME_OR_ID": CONTAINER_NAME_OR_ID,
    }
    missing = [name for name, value in required_variables.items() if not value]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def send_notification(email_msg):
    print("Sending an email notification...")

    message = EmailMessage()
    message["Subject"] = "SITE DOWN"
    message["From"] = EMAIL_ADDRESS
    message["To"] = EMAIL_ADDRESS
    message.set_content(email_msg)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)


def restart_container():
    print("Restarting the Docker container...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=SERVER_IP,
            username=SSH_USERNAME,
            key_filename=SSH_KEY_PATH,
            timeout=20,
        )
        command = f"docker start {shlex.quote(CONTAINER_NAME_OR_ID)}"
        _, stdout, stderr = ssh.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if exit_code != 0:
            raise RuntimeError(error or "Docker could not start the container")
        if output:
            print(output)
    finally:
        ssh.close()

    print("Application container restarted")


def restart_server_and_container():
    print("Rebooting the DigitalOcean droplet...")
    url = (
        "https://api.digitalocean.com/v2/droplets/"
        f"{DIGITAL_OCEAN_DROPLET_ID}/actions"
    )
    headers = {
        "Authorization": f"Bearer {DIGITAL_OCEAN_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json={"type": "reboot"},
        timeout=30,
    )
    response.raise_for_status()
    print("Reboot request accepted. Waiting for SSH to become available...")

    for attempt in range(1, RECOVERY_ATTEMPTS + 1):
        try:
            restart_container()
            return
        except (OSError, paramiko.SSHException, RuntimeError) as error:
            print(f"Recovery attempt {attempt}/{RECOVERY_ATTEMPTS}: {error}")
            time.sleep(10)

    raise RuntimeError("The droplet did not recover within the expected time")


def monitor_application():
    try:
        response = requests.get(APP_URL, timeout=10)
    except requests.RequestException as error:
        print(f"Application is not accessible: {error}")
        send_notification(
            "The application is not accessible. Rebooting the DigitalOcean "
            "droplet and restarting its Docker container."
        )
        restart_server_and_container()
        return

    if response.status_code == 200:
        print("Application is running successfully")
        return

    print(f"Application returned HTTP {response.status_code}")
    send_notification(
        f"The application returned HTTP {response.status_code}. "
        "Restarting its Docker container."
    )

    try:
        restart_container()
    except (OSError, paramiko.SSHException, RuntimeError) as error:
        print(f"Container restart failed: {error}")
        restart_server_and_container()


def main():
    validate_configuration()
    monitor_application()
    schedule.every(MONITOR_INTERVAL_MINUTES).minutes.do(monitor_application)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
