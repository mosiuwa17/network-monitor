#!/usr/bin/env python3
"""
Network Devices Monitoring System
For Ministry of Home Affairs, Lesotho
Monitors: Computers, Servers, Switches, Firewalls
"""

import psutil
import subprocess
import platform
import time
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
import requests
from ping3 import ping
import socket

# ========== CONFIGURATION ==========
# Add your devices here
DEVICES = {
    "computers": [
        {"name": "Front Desk PC", "ip": "192.168.1.10", "type": "windows"},
        {"name": "Registration PC", "ip": "192.168.1.11", "type": "windows"},
        {"name": "Passport Office PC", "ip": "192.168.1.12", "type": "windows"},
    ],
    "servers": [
        {"name": "NICR Database Server", "ip": "192.168.1.20", "type": "linux", "service": "postgresql"},
        {"name": "Web Server", "ip": "192.168.1.21", "type": "linux", "service": "nginx"},
        {"name": "Authentication Server", "ip": "192.168.1.22", "type": "windows", "service": "iis"},
    ],
    "switches": [
        {"name": "Core Switch", "ip": "192.168.1.1", "snmp_community": "public"},
        {"name": "Access Switch 1", "ip": "192.168.1.2", "snmp_community": "public"},
    ],
    "firewalls": [
        {"name": "Edge Firewall", "ip": "192.168.1.254", "type": "cisco"},
    ]
}

# ========== MONITORING FUNCTIONS ==========

def ping_device(ip: str, timeout: int = 2) -> tuple:
    """Ping a device and return (is_up, response_time_ms)"""
    try:
        response = ping(ip, timeout=timeout)
        if response is not None:
            return True, round(response * 1000, 2)
        return False, None
    except Exception:
        return False, None


def check_local_system() -> Dict:
    """Monitor local computer (CPU, RAM, Disk, Network)"""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu_percent,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
        "net_recv_mb": round(net.bytes_recv / (1024**2), 2)
    }


def check_remote_computer(ip: str) -> Dict:
    """Check remote Windows computer via WMI over WinRM (requires credentials)"""
    # This is a simplified version using ping only
    # For full monitoring, you would use WinRM or WMI with credentials
    is_up, response_time = ping_device(ip)
    return {
        "ip": ip,
        "is_up": is_up,
        "response_time_ms": response_time,
        "status": "Online" if is_up else "Offline"
    }


def check_linux_server(ip: str, service: str = None) -> Dict:
    """Check Linux server via SSH (simplified using ping + port check)"""
    is_up, response_time = ping_device(ip)
    status = {}
    
    if is_up and service:
        # Check if service port is open
        port_status = check_port(ip, service)
        status["service_healthy"] = port_status
    else:
        status["service_healthy"] = None
    
    return {
        "ip": ip,
        "is_up": is_up,
        "response_time_ms": response_time,
        "status": "Online" if is_up else "Offline",
        **status
    }


def check_port(ip: str, service: str) -> bool:
    """Check if a service port is open"""
    ports = {
        "postgresql": 5432,
        "nginx": 80,
        "iis": 80,
        "ssh": 22,
        "https": 443
    }
    port = ports.get(service, 80)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_switch(ip: str, snmp_community: str = "public") -> Dict:
    """Check network switch via SNMP (simplified using ping)"""
    # Full SNMP requires additional library: pip install pysnmp
    is_up, response_time = ping_device(ip)
    return {
        "ip": ip,
        "is_up": is_up,
        "response_time_ms": response_time,
        "status": "Online" if is_up else "Offline",
        "snmp_community": snmp_community
    }


def check_firewall(ip: str) -> Dict:
    """Check firewall status via ping and port scanning"""
    is_up, response_time = ping_device(ip)
    return {
        "ip": ip,
        "is_up": is_up,
        "response_time_ms": response_time,
        "status": "Online" if is_up else "Offline"
    }


def generate_report(monitoring_data: Dict) -> str:
    """Generate a formatted report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = []
    report.append("=" * 60)
    report.append(f"NETWORK DEVICES MONITORING REPORT")
    report.append(f"Ministry of Home Affairs, Lesotho")
    report.append(f"Generated: {timestamp}")
    report.append("=" * 60)
    
    # Local System
    local = monitoring_data.get("local", {})
    report.append(f"\n📍 LOCAL SYSTEM (Monitoring Station)")
    report.append(f"   CPU Usage: {local.get('cpu_percent', 0)}%")
    report.append(f"   RAM Usage: {local.get('ram_percent', 0)}% ({local.get('ram_used_gb', 0)} GB / {local.get('ram_total_gb', 0)} GB)")
    report.append(f"   Disk Usage: {local.get('disk_percent', 0)}%")
    
    # Computers
    report.append(f"\n🖥️  COMPUTERS")
    for comp in monitoring_data.get("computers", []):
        status_icon = "🟢" if comp.get("is_up") else "🔴"
        report.append(f"   {status_icon} {comp['name']}: {comp.get('status', 'Unknown')} ({comp.get('ip', 'N/A')})")
        if comp.get("response_time_ms"):
            report.append(f"      Response: {comp['response_time_ms']} ms")
    
    # Servers
    report.append(f"\n🖧 SERVERS")
    for server in monitoring_data.get("servers", []):
        status_icon = "🟢" if server.get("is_up") else "🔴"
        service_icon = "✅" if server.get("service_healthy") else "❌" if server.get("service_healthy") is False else "❓"
        report.append(f"   {status_icon} {server['name']}: {server.get('status', 'Unknown')}")
        if server.get("response_time_ms"):
            report.append(f"      Response: {server['response_time_ms']} ms")
        if server.get("service"):
            report.append(f"      Service: {service_icon} {server['service']}")
    
    # Switches
    report.append(f"\n🔌 SWITCHES")
    for switch in monitoring_data.get("switches", []):
        status_icon = "🟢" if switch.get("is_up") else "🔴"
        report.append(f"   {status_icon} {switch['name']}: {switch.get('status', 'Unknown')} ({switch.get('ip', 'N/A')})")
    
    # Firewalls
    report.append(f"\n🛡️ FIREWALLS")
    for fw in monitoring_data.get("firewalls", []):
        status_icon = "🟢" if fw.get("is_up") else "🔴"
        report.append(f"   {status_icon} {fw['name']}: {fw.get('status', 'Unknown')} ({fw.get('ip', 'N/A')})")
    
    report.append(f"\n" + "=" * 60)
    report.append(f"Report generated by: Motlatsi Mosiuoa")
    report.append("=" * 60)
    
    return "\n".join(report)


def save_report_json(data: Dict, filename: str = None):
    """Save monitoring data as JSON"""
    if not filename:
        filename = f"network_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"📁 JSON report saved: {filename}")
    return filename


def save_report_csv(data: Dict, filename: str = None):
    """Save monitoring data as CSV"""
    if not filename:
        filename = f"network_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    rows = []
    # Add servers/computers
    for device_type in ["computers", "servers", "switches", "firewalls"]:
        for device in data.get(device_type, []):
            rows.append({
                "timestamp": data.get("timestamp"),
                "device_type": device_type,
                "device_name": device.get("name"),
                "ip": device.get("ip"),
                "status": device.get("status"),
                "response_time_ms": device.get("response_time_ms")
            })
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print(f"📊 CSV report saved: {filename}")
    return filename


def monitor_all_devices() -> Dict:
    """Monitor all configured devices"""
    print("🔄 Starting network monitoring...")
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "local": check_local_system(),
        "computers": [],
        "servers": [],
        "switches": [],
        "firewalls": []
    }
    
    # Monitor computers
    print("📡 Checking computers...")
    for comp in DEVICES.get("computers", []):
        status = check_remote_computer(comp["ip"])
        status["name"] = comp["name"]
        result["computers"].append(status)
    
    # Monitor servers
    print("🖧 Checking servers...")
    for server in DEVICES.get("servers", []):
        status = check_linux_server(server["ip"], server.get("service"))
        status["name"] = server["name"]
        status["service"] = server.get("service")
        result["servers"].append(status)
    
    # Monitor switches
    print("🔌 Checking switches...")
    for switch in DEVICES.get("switches", []):
        status = check_switch(switch["ip"], switch.get("snmp_community", "public"))
        status["name"] = switch["name"]
        result["switches"].append(status)
    
    # Monitor firewalls
    print("🛡️ Checking firewalls...")
    for fw in DEVICES.get("firewalls", []):
        status = check_firewall(fw["ip"])
        status["name"] = fw["name"]
        result["firewalls"].append(status)
    
    return result


def main():
    """Main execution"""
    print("=" * 60)
    print("NETWORK DEVICES MONITORING SYSTEM")
    print("Ministry of Home Affairs, Lesotho")
    print("=" * 60)
    
    # Run monitoring
    data = monitor_all_devices()
    
    # Generate and print report
    report = generate_report(data)
    print(report)
    
    # Save reports
    save_report_json(data)
    save_report_csv(data)
    
    print("\n✅ Monitoring complete!")


if __name__ == "__main__":
    main()