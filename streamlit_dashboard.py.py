import streamlit as st
import pandas as pd
import subprocess
import json
import os
from datetime import datetime

st.set_page_config(page_title="Network Monitor - Home Affairs", layout="wide")

st.title("🖧 Network Devices Monitoring System")
st.caption("Ministry of Home Affairs, Lesotho")

# Run monitoring
if st.button("🔄 Run Network Scan"):
    with st.spinner("Scanning network devices..."):
        result = subprocess.run(["python", "network_monitor.py"], capture_output=True, text=True)
        
        # Find the latest JSON report
        files = [f for f in os.listdir() if f.startswith("network_report_") and f.endswith(".json")]
        if files:
            latest = max(files, key=os.path.getctime)
            with open(latest, 'r') as f:
                data = json.load(f)
            
            # Display local system metrics
            st.subheader("💻 Local System")
            local = data.get("local", {})
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("CPU Usage", f"{local.get('cpu_percent', 0)}%")
            col2.metric("RAM Usage", f"{local.get('ram_percent', 0)}%")
            col3.metric("Disk Usage", f"{local.get('disk_percent', 0)}%")
            col4.metric("Last Scan", datetime.now().strftime("%H:%M:%S"))
            
            # Servers
            st.subheader("🖧 Servers")
            servers_df = pd.DataFrame(data.get("servers", []))
            if not servers_df.empty:
                st.dataframe(servers_df)
            
            # Computers
            st.subheader("🖥️ Computers")
            computers_df = pd.DataFrame(data.get("computers", []))
            if not computers_df.empty:
                st.dataframe(computers_df)
            
            # Switches
            st.subheader("🔌 Switches")
            switches_df = pd.DataFrame(data.get("switches", []))
            if not switches_df.empty:
                st.dataframe(switches_df)
            
            # Firewalls
            st.subheader("🛡️ Firewalls")
            firewalls_df = pd.DataFrame(data.get("firewalls", []))
            if not firewalls_df.empty:
                st.dataframe(firewalls_df)
            
            st.success(f"✅ Scan complete! {len(servers_df) + len(computers_df)} devices checked.")
        else:
            st.error("No report found. Run the script first.")

st.info("This tool monitors computers, servers, switches, and firewalls. Reports are saved as JSON and CSV.")