# Python Automation for DevOps Projects 🐍 🚀

This repository contains a collection of Python scripts designed to automate common DevOps tasks, focusing on AWS infrastructure management, monitoring, and cloud resource handling. These projects were developed as part of a DevOps Bootcamp module to demonstrate the power of Python in automation.

---

### 🛠 Technologies Used
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230080FF.svg?style=for-the-badge&logo=digitalocean&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Boto3](https://img.shields.io/badge/Boto3-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)

---

### 📂 Projects Overview

| Script Name | Description |
| :--- | :--- |
| **`monitor-website.py`** | Monitors a web application hosted on DigitalOcean, sends email alerts via SMTP if it's down, and automatically restarts Docker containers or reboots the server. |
| **`ec2-status-checks.py`** | Regularly checks the status of AWS EC2 instances and prints their health information. |
| **`eks-status-checks.py`** | Retrieves and displays information about AWS EKS clusters, including status, endpoint, and version. |
| **`create-vpc.py`** | Automates the creation of an AWS VPC along with public and private subnets. |
| **`add-env-tags.py`** | Massively applies environment tags (e.g., `prod`, `dev`) to EC2 instances across different AWS regions (Sydney and Singapore). |
| **`volume-backups.py`** | Automates daily snapshots for AWS EBS volumes tagged with specific names (e.g., `prod`). |
| **`cleanup-snapshots.py`** | Manages storage costs by deleting old AWS EBS snapshots, keeping only the most recent ones for each volume. |
| **`restore-volume.py`** | Restores an EBS volume from its latest available snapshot. |

---

### 🚀 Getting Started

#### 1. Prerequisites
Ensure you have Python 3.x installed on your machine.

#### 2. Install Dependencies
Install the required libraries using pip:
```bash
pip install boto3 requests paramiko schedule
```

#### 3. Configuration
For scripts interacting with AWS, ensure you have your credentials configured:
```bash
aws configure
```

For the **`monitor-website.py`** script, set the following environment variables:
- `EMAIL_ADDRESS`: Your Gmail address.
- `EMAIL_PASSWORD`: Your Gmail app-specific password.
- `DIGITAL_OCEAN_TOKEN`: Your DigitalOcean API token.
- `DIGITAL_OCEAN_DROPLET_ID`: The ID of your droplet.

---

### 🔧 Usage
Run any script directly from the terminal:
```bash
python monitor-website.py
```
```bash
python volume-backups.py
```

---
*Created as part of Automation with Python Module.*
