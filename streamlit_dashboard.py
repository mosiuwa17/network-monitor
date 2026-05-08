import streamlit as st
import subprocess
import json
import os
from datetime import datetime

st.set_page_config(page_title="Network Monitor - Home Affairs", layout="wide")

st.title("🖧 Network Devices Monitoring System")
st.caption("Ministry of Home Affairs, Lesotho")

# Device list (update with your actual IPs)
devices = {
    "🖧 Servers": [
        {"name": "NICR Database Server", "ip": "8.8.8.8"},
        {"name": "Web Server", "ip": "8.8.4.4"},
    ],
    "🖥️ Computers": [
        {"name": "Front Desk PC", "ip": "1.1.1.1"},
        {"name": "Registration PC", "ip": "1.0.0.1"},
    ],
    "🔌 Switches": [
        {"name": "Core Switch", "ip": "8.8.8.8"},
    ],
    "🛡️ Firewalls": [
        {"name": "Edge Firewall", "ip": "1.1.1.1"},
    ]
}

def ping_ip(ip):
    """Ping an IP address"""
    param = '-n' if os.name == 'nt' else '-c'
    command = ['ping', param, '1', ip]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

st.subheader("📡 Real-time Device Status")

if st.button("🔄 Run Network Scan"):
    with st.spinner("Scanning network devices..."):
        for category, device_list in devices.items():
            st.subheader(category)
            for device in device_list:
                is_up = ping_ip(device["ip"])
                status = "🟢 Online" if is_up else "🔴 Offline"
                st.write(f"{status} **{device['name']}** ({device['ip']})")
        st.success(f"✅ Scan completed at {datetime.now().strftime('%H:%M:%S')}")
else:
    st.info("Click 'Run Network Scan' to check device status.")

st.caption("Note: Using public DNS IPs (8.8.8.8, 1.1.1.1) as placeholders. Replace with actual device IPs in production.")
