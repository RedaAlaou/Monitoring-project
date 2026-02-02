# Computer Performance Monitor

Real-time system monitoring client that sends CPU, RAM, GPU, and Disk metrics to the IoT platform.

## Features

- **CPU Monitoring**: Overall usage + per-core breakdown
- **Memory Monitoring**: RAM usage in MB and percentage
- **Disk Monitoring**: Disk space utilization percentage
- **Network Monitoring**: Bytes sent/received since boot
- **GPU Monitoring**: NVIDIA GPU usage and VRAM (optional, requires NVIDIA GPU)
- **Auto-registration**: Creates and deploys device automatically
- **Configurable**: Environment variables for all settings

## Installation

1. **Install dependencies**:
   ```bash
   cd end-devices
   pip install -r requirements.txt
   ```

2. **For NVIDIA GPU support** (optional):
   - Install NVIDIA drivers
   - `pip install GPUtil`

## Usage

### Basic Usage

```bash
python computer_monitor.py
```

### Configuration via Environment Variables

```bash
# Backend URLs
export SIGNING_SERVICE_URL="http://localhost:8000"
export DEVICE_MANAGEMENT_URL="http://localhost:8001"

# Device configuration
export DEVICE_NAME="My-Computer"
export DEVICE_SERIAL="PC-CUSTOM-001"
export DEVICE_LOCATION="Home Office"

# Monitoring interval (seconds)
export MONITORING_INTERVAL="5"

python computer_monitor.py
```

## Output Example

```
============================================================
Computer Performance Monitor
============================================================
✓ GPU monitoring enabled (NVIDIA)
✓ Authenticated as admin@example.com
✓ Device created: Computer-DESKTOP-ABC (ID: 5)
✓ Device deployed (ID: 5)

✓ Monitoring started (interval: 5s)
  Device ID: 5
  Device Name: Computer-DESKTOP-ABC
  Serial: PC-DESKTOP-ABC
  Type: computer

Press Ctrl+C to stop...

[10:30:05] Telemetry #1 sent | CPU: 45.2% | RAM: 68.5% | Disk: 72.3% | GPU: 30.1%
[10:30:10] Telemetry #2 sent | CPU: 42.8% | RAM: 68.7% | Disk: 72.3% | GPU: 28.5%
[10:30:15] Telemetry #3 sent | CPU: 48.5% | RAM: 69.2% | Disk: 72.3% | GPU: 35.2%
```

## Metrics Collected

| Metric | Description | Unit |
|--------|-------------|------|
| `cpu_usage` | Overall CPU utilization | % |
| `cpu_per_core` | Per-core CPU utilization | Array of % |
| `ram_used_mb` | RAM used | MB |
| `ram_percent` | RAM utilization | % |
| `disk_usage_percent` | Disk space used | % |
| `network_sent_mb` | Total bytes sent | MB |
| `network_recv_mb` | Total bytes received | MB |
| `gpu_usage` | GPU utilization (NVIDIA only) | % |
| `gpu_memory_used_mb` | VRAM used (NVIDIA only) | MB |
| `gpu_temperature` | GPU temperature (NVIDIA only) | °C |

## Frontend Visualization

Telemetry is displayed in the **System Monitoring** page (`/system-monitoring`):

- **KPI Cards**: Current CPU, RAM, GPU, Disk usage
- **CPU Chart**: Timeline of CPU usage
- **RAM Chart**: Memory utilization over time
- **GPU/Disk Chart**: Combined metrics
- **Advanced Metrics**: Per-core CPU, VRAM, Network I/O

## Troubleshooting

### GPU not detected
- **Problem**: `⚠ GPU monitoring unavailable`
- **Solution**: Install `pip install GPUtil` and ensure NVIDIA drivers are installed
- **Note**: GPU metrics are optional; monitor works without GPU

### Authentication failed
- **Problem**: `✗ Authentication failed: 401`
- **Solution**: Check credentials in `authenticate()` method or set env vars:
  ```bash
  export AUTH_USERNAME="your-email@example.com"
  export AUTH_PASSWORD="your-password"
  ```

### Connection refused
- **Problem**: `✗ Telemetry send error: Connection refused`
- **Solution**: Ensure backend services are running:
  ```bash
  docker-compose ps
  docker-compose up -d
  ```

### High CPU usage
- **Problem**: Monitor consuming too much CPU
- **Solution**: Increase `MONITORING_INTERVAL` (e.g., 10 or 30 seconds)

## Device Type

The computer monitor uses device type `computer`, which is displayed in the **System Monitoring** page. Other device types:

- `iot_sensor`, `iot_gateway`, `iot_actuator` → **IoT Monitoring** page
- `server`, `edge_device`, `gpu_node` → **System Monitoring** page

## Architecture

```
Computer Monitor (Python)
    ↓ [Authenticate]
Signing Service (:8000)
    ↓ [JWT Token]
Computer Monitor
    ↓ [Create/Deploy Device]
Device Management (:8001)
    ↓ [Send Telemetry every 5s]
Device Management (:8001)
    ↓ [RabbitMQ publish]
Monitoring Service (:8002)
    ↓ [MongoDB + Socket.IO]
Frontend React App
```

## Development

To modify monitoring metrics, edit the `read_system_metrics()` method in `computer_monitor.py`.

### Adding New Metrics

```python
def read_system_metrics(self) -> Dict:
    metrics = {
        # ... existing metrics ...
        
        # Add custom metric
        "battery_percent": psutil.sensors_battery().percent if psutil.sensors_battery() else None,
    }
    return metrics
```

## License

MIT License - See main project LICENSE file
