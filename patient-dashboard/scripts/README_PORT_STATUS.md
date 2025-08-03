# All Ports Status

## Overview
A simple shell script that shows ALL active localhost ports with their process information and status.

## Quick Start
```bash
# Run the script
./all-ports.sh
```

## Output Example
```
Port 3000   - PID: 53764   - Process: next-server          - Status: Running
Port 3001   - PID: 55888   - Process: next-server          - Status: Running
Port 5000   - PID: 621     - Process: ControlCenter        - Status: Running
Port 5432   - PID: 782     - Process: postgres             - Status: Running
Port 6379   - PID: 773     - Process: redis-server         - Status: Running
Port 6443   - PID: 9589    - Process: com.docker.backend   - Status: Running
Port 7000   - PID: 621     - Process: ControlCenter        - Status: Running
Port 8000   - PID: 81311   - Process: surreal              - Status: Running
Port 8001   - PID: 54758   - Process: Python               - Status: Running
Port 8811   - PID: 9589    - Process: com.docker.backend   - Status: Running
Port 57246  - PID: 631     - Process: rapportd             - Status: Running
```

## What It Shows
- **Port**: The port number
- **PID**: Process ID of the service
- **Process**: Name of the process running on that port
- **Status**: Current status (Running for all active ports)

## Common Services for Patient Dashboard
- **Port 3000**: Frontend (Next.js)
- **Port 8000**: SurrealDB
- **Port 8001**: Backend API (Python/FastAPI)

## Usage

### Basic Usage
```bash
cd ~/devqai/pfinni_dashboard
./all-ports.sh
```

### Make It Available Globally
```bash
# Copy to a directory in your PATH
sudo cp all-ports.sh /usr/local/bin/ports
sudo chmod +x /usr/local/bin/ports

# Now run from anywhere
ports
```

### Add Alias
Add to your `~/.zshrc` or `~/.bashrc`:
```bash
alias ports='~/devqai/pfinni_dashboard/all-ports.sh'
```

## Troubleshooting

### Script Not Executable
```bash
chmod +x all-ports.sh
```

### Permission Errors
Some system processes may require elevated permissions:
```bash
sudo ./all-ports.sh
```

### Check Specific Port
```bash
lsof -i :3000
```

### Kill Process on Port
```bash
# Find PID from all-ports.sh output, then:
kill <PID>

# Or force kill
kill -9 <PID>
```

## Dependencies
- `lsof` - List open files (pre-installed on macOS/Linux)
- `ps` - Process status (pre-installed on macOS/Linux)
- `grep`, `awk`, `sort` - Text processing (pre-installed)

## Why Use This?
- Quickly see what's actually running before starting/stopping services
- Avoid port conflicts
- Identify unknown services using your ports
- Troubleshoot connection issues