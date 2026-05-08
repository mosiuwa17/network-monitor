import streamlit as st
import subprocess
import platform
import json
import os
from datetime import datetime

st.set_page_config(page_title="Network Monitor - Home Affairs", layout="wide")

st.title("🖧 Network Devices Monitoring System")
st.caption("Ministry of Home Affairs, Lesotho")

# Device list - REPLACE THESE IPs WITH YOUR ACTUAL DEVICE IPs
devices = {
    "🖧 Servers": [
        {"name": "NICR Database Server", "ip": "192.168.1.20"},
        {"name": "Web Server", "ip": "192.168.1.21"},
    ],
    "🖥️ Computers": [
        {"name": "Front Desk PC", "ip": "192.168.1.10"},
        {"name": "Registration PC", "ip": "192.168.1.11"},
    ],
    "🔌 Switches": [
        {"name": "Core Switch", "ip": "192.168.1.1"},
    ],
    "🛡️ Firewalls": [
        {"name": "Edge Firewall", "ip": "192.168.1.254"},
    ]
}

def ping_ip(ip):
    """Ping an IP address - works on Windows, Mac, Linux"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

st.subheader("📡 Real-time Device Status")

if st.button("🔄 Run Network Scan"):
    with st.spinner("Scanning network devices..."):
        results = []
        for category, device_list in devices.items():
            st.subheader(category)
            for device in device_list:
                is_up = ping_ip(device["ip"])
                status = "🟢 Online" if is_up else "🔴 Offline"
                st.write(f"{status} **{device['name']}** ({device['ip']})")
                results.append({
                    "category": category,
                    "name": device["name"],
                    "ip": device["ip"],
                    "status": "Online" if is_up else "Offline",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Save results to JSON
        with open("scan_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        st.success(f"✅ Scan completed at {datetime.now().strftime('%H:%M:%S')}")
        st.download_button(
            label="📊 Download Results (JSON)",
            data=json.dumps(results, indent=2),
            file_name=f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
else:
    st.info("Click 'Run Network Scan' to check device status.")

st.caption("Note: Replace the IP addresses in the code with your actual device IPs.")
