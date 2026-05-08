# Network Devices Monitoring System

A comprehensive network monitoring solution for the Ministry of Home Affairs, Lesotho. Monitors computers, servers, switches, and firewalls with real-time status reporting.

## 🛠️ Tech Stack

- **Python 3.9+**
- **psutil** - System monitoring (CPU, RAM, Disk)
- **ping3** - Network connectivity testing
- **Streamlit** - Web dashboard (optional)

## ✨ Features

- Monitor local system (CPU, RAM, Disk, Network I/O)
- Ping remote devices (computers, servers, switches, firewalls)
- Check service ports (PostgreSQL, Nginx, IIS, SSH)
- Generate daily/weekly reports (JSON and CSV)
- Optional web dashboard with Streamlit
- Email alerts for offline devices (can be added)

## 📦 Installation

```bash
git clone https://github.com/mosiuwa17/network-monitor
cd network-monitor
pip install -r requirements.txt