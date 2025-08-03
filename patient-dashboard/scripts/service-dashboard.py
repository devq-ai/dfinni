#!/usr/bin/env python3
"""
Service Dashboard - Real-time monitoring of localhost services
Provides a web interface to monitor and manage local development services
"""

import os
import sys
import json
import time
import psutil
import socket
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from threading import Thread
import signal

# Add FastAPI for web interface
try:
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets", "psutil"])
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    import uvicorn

app = FastAPI(title="Service Dashboard")

# Service configuration
SERVICES = {
    3000: {
        "name": "Frontend (Next.js)",
        "start_cmd": "cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/frontend && npm run dev",
        "health_check": "http://localhost:3000",
        "critical": True
    },
    8000: {
        "name": "Backend API (FastAPI)",
        "start_cmd": "cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/backend && ./start_server.sh",
        "health_check": "http://localhost:8000/health",
        "critical": True
    },
    8001: {
        "name": "Backend API (Alt)",
        "start_cmd": None,  # Alternative port, no auto-start
        "health_check": "http://localhost:8001/health",
        "critical": False
    },
    8080: {
        "name": "SurrealDB",
        "start_cmd": "cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard && docker-compose up -d surrealdb",
        "health_check": None,
        "critical": True
    },
    9090: {
        "name": "Prometheus",
        "start_cmd": "cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard && docker-compose up -d prometheus",
        "health_check": "http://localhost:9090",
        "critical": False
    },
    3001: {
        "name": "Grafana",
        "start_cmd": "cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard && docker-compose up -d grafana",
        "health_check": "http://localhost:3001",
        "critical": False
    }
}

class ServiceMonitor:
    def __init__(self):
        self.services_status = {}
        self.update_status()
    
    def check_port(self, port: int) -> Tuple[bool, Optional[int], Optional[str]]:
        """Check if a port is in use and get process info"""
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    return True, conn.pid, process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return True, conn.pid, "Unknown"
        return False, None, None
    
    def get_process_info(self, pid: int) -> Dict:
        """Get detailed process information"""
        try:
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
                "cmdline": " ".join(process.cmdline()[:3])  # First 3 parts of command
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"pid": pid, "error": "Access denied or process not found"}
    
    def update_status(self):
        """Update the status of all services"""
        for port, config in SERVICES.items():
            is_running, pid, process_name = self.check_port(port)
            
            status = {
                "port": port,
                "name": config["name"],
                "running": is_running,
                "critical": config["critical"],
                "timestamp": datetime.now().isoformat()
            }
            
            if is_running and pid:
                status["process"] = self.get_process_info(pid)
            
            self.services_status[port] = status
        
        # Check for unknown services
        self.check_unknown_services()
    
    def check_unknown_services(self):
        """Find services running on localhost that aren't in our config"""
        known_ports = set(SERVICES.keys())
        
        for conn in psutil.net_connections(kind='inet'):
            if (conn.laddr.ip in ['127.0.0.1', '::1'] and 
                conn.status == 'LISTEN' and 
                conn.laddr.port not in known_ports and
                1024 < conn.laddr.port < 65535):  # Ignore system ports
                
                try:
                    process = psutil.Process(conn.pid)
                    self.services_status[conn.laddr.port] = {
                        "port": conn.laddr.port,
                        "name": f"Unknown ({process.name()})",
                        "running": True,
                        "critical": False,
                        "unknown": True,
                        "process": self.get_process_info(conn.pid),
                        "timestamp": datetime.now().isoformat()
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    
    def start_service(self, port: int) -> bool:
        """Start a service by port"""
        if port in SERVICES and SERVICES[port]["start_cmd"]:
            try:
                subprocess.Popen(SERVICES[port]["start_cmd"], shell=True)
                time.sleep(3)  # Give service time to start
                return True
            except Exception as e:
                print(f"Failed to start service on port {port}: {e}")
                return False
        return False
    
    def stop_service(self, port: int) -> bool:
        """Stop a service by port"""
        is_running, pid, _ = self.check_port(port)
        if is_running and pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Failed to stop service on port {port}: {e}")
                return False
        return False

monitor = ServiceMonitor()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Service Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #fff;
            margin-bottom: 30px;
        }
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .service-card {
            background: #141414;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 20px;
            position: relative;
        }
        .service-card.running {
            border-color: #10b981;
        }
        .service-card.stopped {
            border-color: #ef4444;
        }
        .service-card.unknown {
            border-color: #f59e0b;
        }
        .status-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .status-indicator.running {
            background: #10b981;
            animation: pulse 2s infinite;
        }
        .status-indicator.stopped {
            background: #ef4444;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .service-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .service-port {
            color: #9ca3af;
            margin-bottom: 15px;
        }
        .service-details {
            font-size: 14px;
            color: #9ca3af;
        }
        .service-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        button {
            background: #3e3e3e;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #4b5563;
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .refresh-info {
            text-align: center;
            color: #6b7280;
            margin-top: 20px;
        }
        .unknown-services {
            margin-top: 40px;
        }
        .process-info {
            margin-top: 10px;
            padding: 10px;
            background: #0f0f0f;
            border-radius: 4px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Service Dashboard</h1>
        <div id="services" class="service-grid"></div>
        <div id="unknown-services" class="unknown-services"></div>
        <div class="refresh-info">Auto-refreshing every 5 seconds</div>
    </div>
    
    <script>
        let ws = new WebSocket("ws://localhost:8888/ws");
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
        
        function updateDashboard(services) {
            const container = document.getElementById('services');
            const unknownContainer = document.getElementById('unknown-services');
            container.innerHTML = '';
            unknownContainer.innerHTML = '';
            
            const knownServices = [];
            const unknownServices = [];
            
            Object.values(services).forEach(service => {
                if (service.unknown) {
                    unknownServices.push(service);
                } else {
                    knownServices.push(service);
                }
            });
            
            // Render known services
            knownServices.sort((a, b) => a.port - b.port).forEach(service => {
                container.innerHTML += createServiceCard(service);
            });
            
            // Render unknown services
            if (unknownServices.length > 0) {
                unknownContainer.innerHTML = '<h2>Unknown Services</h2><div class="service-grid">';
                unknownServices.sort((a, b) => a.port - b.port).forEach(service => {
                    unknownContainer.innerHTML += createServiceCard(service);
                });
                unknownContainer.innerHTML += '</div>';
            }
        }
        
        function createServiceCard(service) {
            const statusClass = service.running ? 'running' : 'stopped';
            const processInfo = service.process ? `
                <div class="process-info">
                    PID: ${service.process.pid} | 
                    CPU: ${service.process.cpu_percent?.toFixed(1) || 0}% | 
                    Memory: ${service.process.memory_mb?.toFixed(1) || 0} MB
                    ${service.process.cmdline ? '<br>Cmd: ' + service.process.cmdline : ''}
                </div>
            ` : '';
            
            return `
                <div class="service-card ${statusClass} ${service.unknown ? 'unknown' : ''}">
                    <div class="status-indicator ${statusClass}"></div>
                    <div class="service-name">${service.name}</div>
                    <div class="service-port">Port: ${service.port}</div>
                    <div class="service-details">
                        Status: ${service.running ? 'Running' : 'Stopped'}
                        ${service.critical ? ' (Critical Service)' : ''}
                    </div>
                    ${processInfo}
                    <div class="service-actions">
                        ${!service.unknown ? `
                            <button onclick="controlService(${service.port}, 'start')" 
                                    ${service.running ? 'disabled' : ''}>Start</button>
                            <button onclick="controlService(${service.port}, 'stop')"
                                    ${!service.running ? 'disabled' : ''}>Stop</button>
                        ` : `
                            <button onclick="controlService(${service.port}, 'stop')"
                                    ${!service.running ? 'disabled' : ''}>Kill Process</button>
                        `}
                    </div>
                </div>
            `;
        }
        
        async function controlService(port, action) {
            try {
                const response = await fetch(`/service/${port}/${action}`, { method: 'POST' });
                const result = await response.json();
                if (!result.success) {
                    alert(`Failed to ${action} service on port ${port}`);
                }
            } catch (error) {
                console.error('Control error:', error);
            }
        }
        
        // Initial load
        fetch('/status').then(r => r.json()).then(updateDashboard);
    </script>
</body>
</html>
"""

@app.get("/status")
async def get_status():
    """Get current status of all services"""
    monitor.update_status()
    return monitor.services_status

@app.post("/service/{port}/{action}")
async def control_service(port: int, action: str):
    """Start or stop a service"""
    if action == "start":
        success = monitor.start_service(port)
    elif action == "stop":
        success = monitor.stop_service(port)
    else:
        return {"success": False, "error": "Invalid action"}
    
    monitor.update_status()
    return {"success": success}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    try:
        while True:
            monitor.update_status()
            await websocket.send_json(monitor.services_status)
            await asyncio.sleep(5)
    except Exception:
        pass

if __name__ == "__main__":
    import asyncio
    print("🚀 Starting Service Dashboard on http://localhost:8888")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="warning")