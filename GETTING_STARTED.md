# Getting Started Guide

Complete setup instructions for deploying Pan-Dashboard on a fresh Linux server.

---

## Prerequisites

- Linux server (Ubuntu 20.04+, RHEL 8+, or similar)
- Root or sudo access
- 20+ GB free disk space
- Internet connection

---

## Step 1: Install Docker

### Ubuntu/Debian:
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

### RHEL/Rocky/AlmaLinux:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

---

## Step 2: Install Python 3

### Ubuntu/Debian:
```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

### RHEL/Rocky/AlmaLinux:
```bash
sudo dnf install -y python3 python3-pip
python3 --version
```

---

## Step 3: Transfer Project Files

### Option A: Using SCP (from your Mac)
```bash
# From your Mac, transfer the project folder
cd /Users/microbarley/visualstudio/
tar czf pan-dashboard.tar.gz pan-dashboard/
scp pan-dashboard.tar.gz user@server:/home/user/

# On Linux server
cd /home/user/
tar xzf pan-dashboard.tar.gz
cd pan-dashboard
```

### Option B: Using rsync (from your Mac)
```bash
# From your Mac
rsync -avz --progress /Users/microbarley/visualstudio/pan-dashboard/ user@server:/home/user/pan-dashboard/

# On Linux server
cd /home/user/pan-dashboard
```

### Option C: Using Git
```bash
# On Linux server
cd /home/user/
git clone <your-repo-url> pan-dashboard
cd pan-dashboard

# Copy CSV file separately (too large for git)
# Use scp or rsync for the CSV file
```

---

## Step 4: Setup Python Environment (Optional)

**Note:** This step is optional if you plan to use the containerized importer (recommended for macvlan networking).

```bash
# Navigate to project directory
cd /home/user/pan-dashboard

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Step 5: Verify CSV File

```bash
# Check CSV file exists
ls -lh docker/data/symphony_scan.csv

# Should show something like:
# -rw-r--r-- 1 user user 13G Oct 8 12:00 docker/data/symphony_scan.csv
```

**If CSV is missing:**
- Transfer it from your Mac using `scp` or `rsync`
- Place it in the `docker/data/` directory
- Rename it to `symphony_scan.csv` if needed

---

## Step 6: Start Docker Containers

```bash
# Navigate to docker directory
cd /home/user/pan-dashboard/docker

# Start containers in background
docker compose up -d

# Wait 10 seconds for containers to initialize
sleep 10

# Verify containers are running
docker ps

# Should show:
# pan-clickhouse (up)
# pan-grafana (up)
```

**Check logs if needed:**
```bash
docker compose logs clickhouse
docker compose logs grafana
```

---

## Step 7: Create Database Schema

```bash
# Navigate to project root
cd /home/user/pan-dashboard

# Create the database schema
cat scripts/create_schema.sql | docker exec -i pan-clickhouse clickhouse-client --password clickhouse

# Verify schema was created
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SHOW TABLES FROM file_share"

# Should output:
# file_scan
```

---

## Step 8: Import Data

### Option A: Container Importer (Recommended for Macvlan)

**Use this method if using macvlan networking or if the host cannot reach containers.**

```bash
# Navigate to docker directory
cd /home/user/pan-dashboard/docker

# Run the containerized importer
docker compose run --rm importer

# This will take 2-3 minutes for 24M rows
# You'll see progress updates every 100k rows
```

### Option B: Local Python Script (For Bridge Networking)

**Use this method if containers are accessible from the host (bridge or host networking).**

```bash
# Make sure you're in the project root
cd /home/user/pan-dashboard

# Activate virtual environment
source venv/bin/activate

# Run import script
python scripts/import_data.py

# This will take 2-3 minutes for 24M rows
# You'll see progress updates every 100k rows
```

### Why Two Methods?

- **Macvlan networking:** Docker host cannot communicate directly with macvlan containers. The container importer runs inside the ClickHouse network namespace, avoiding this limitation.
- **Bridge networking:** Host can reach containers via localhost or port mappings. Local Python script works fine.

**Expected output (both methods):**
```
Connecting to ClickHouse at localhost:8123...
Successfully connected to ClickHouse

Processing CSV file: ../data/symphony_scan.csv
Skipping 4 header lines...

Importing data in batches of 10,000...
Processed 10,000 rows...
Processed 20,000 rows...
...
Processed 24,250,000 rows...

✓ Import completed successfully!
Total rows imported: 24,257,739
Time elapsed: 147.3 seconds
Average speed: 164,691 rows/second
```

---

## Step 9: Verify Data Import

```bash
# Check row count
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT COUNT(*) FROM file_share.file_scan"

# Should show: 24257739 (or similar)

# Check sample data
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT path, filename, size FROM file_share.file_scan LIMIT 5"
```

---

## Step 10: Access Grafana

### Open Grafana in Browser:
```
http://YOUR_SERVER_IP:3000
```

**Default Login:**
- Username: `admin`
- Password: `panzura`

### Navigate to Dashboards:
1. Click "Dashboards" in left menu
2. Click "File Share" folder
3. Select any dashboard to view

**Available Dashboards:**
- Executive Overview - File Share Analytics
- Deep Dive - Data Explorer
- File Aging & Stale Data Analysis
- Storage Optimization
- User & Owner Analysis
- Security & Permissions Analysis

---

## Step 11: Firewall Configuration (if needed)

### Ubuntu (UFW):
```bash
# Allow Grafana port
sudo ufw allow 3000/tcp

# Check status
sudo ufw status
```

### RHEL/Rocky (firewalld):
```bash
# Allow Grafana port
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-ports
```

---

## Troubleshooting

### Containers won't start:
```bash
# Check Docker is running
sudo systemctl status docker

# Check logs
cd /home/user/pan-dashboard/docker
docker compose logs

# Restart containers
docker compose restart
```

### Can't connect to Grafana:
```bash
# Check if Grafana is running
docker ps | grep pan-grafana

# Check port is accessible
curl http://localhost:3000

# Check firewall
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # RHEL
```

### Import script fails:
```bash
# Verify CSV file exists
ls -lh data/symphony_scan.csv

# Check ClickHouse is running
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT 1"

# Check Python dependencies
source venv/bin/activate
pip list | grep clickhouse
```

### Dashboard shows "No data":
```bash
# Check data exists
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT COUNT(*) FROM file_share.file_scan"

# Restart Grafana
docker compose restart grafana
```

---

## Management Commands

### Stop containers:
```bash
cd /home/user/pan-dashboard/docker
docker compose down
```

### Start containers:
```bash
cd /home/user/pan-dashboard/docker
docker compose up -d
```

### Restart containers:
```bash
cd /home/user/pan-dashboard/docker
docker compose restart
```

### View logs:
```bash
cd /home/user/pan-dashboard/docker
docker compose logs -f
```

### Check disk usage:
```bash
docker system df -v
```

### Backup ClickHouse data:
```bash
docker run --rm -v docker_clickhouse_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/clickhouse_backup.tar.gz -C /data .
```

---

## Service Management (Optional)

To auto-start containers on system boot:

### Create systemd service:
```bash
sudo nano /etc/systemd/system/pan-dashboard.service
```

**Add this content:**
```ini
[Unit]
Description=Pan Dashboard
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/pan-dashboard/docker
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=user

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable pan-dashboard
sudo systemctl start pan-dashboard
```

---

## Performance Tuning

### For large datasets (50M+ rows):

**Increase batch size in import script:**
```bash
# Edit scripts/import_data.py
# Change: BATCH_SIZE = 10000
# To:     BATCH_SIZE = 50000
```

**Allocate more memory to ClickHouse:**
```yaml
# In docker/docker-compose.yml, add to clickhouse service:
environment:
  - CLICKHOUSE_MAX_MEMORY_USAGE=8000000000  # 8GB
```

---

## Security Hardening

### Change default passwords:

**Grafana:**
```bash
# Edit docker/docker-compose.yml
# Change: GF_SECURITY_ADMIN_PASSWORD=panzura
# To:     GF_SECURITY_ADMIN_PASSWORD=YourStrongPassword

docker compose restart grafana
```

**ClickHouse:**
```bash
# Edit docker/docker-compose.yml
# Change: CLICKHOUSE_PASSWORD=clickhouse
# To:     CLICKHOUSE_PASSWORD=YourStrongPassword

# Update datasource config in:
# docker/grafana/provisioning/datasources/clickhouse.yml

docker compose restart
```

### Use HTTPS (recommended for production):

Set up a reverse proxy (Nginx or Caddy) with SSL certificates:
```bash
# Example with Caddy (automatic HTTPS)
sudo apt install caddy

# Create Caddyfile:
sudo nano /etc/caddy/Caddyfile
```

**Add:**
```
dashboard.yourdomain.com {
    reverse_proxy localhost:3000
}
```

```bash
sudo systemctl restart caddy
```

---

## Quick Reference

| Component | Port | URL | Credentials |
|-----------|------|-----|-------------|
| Grafana | 3000 | http://server:3000 | admin/panzura |
| ClickHouse HTTP | 8123 | http://server:8123 | default/clickhouse |
| ClickHouse Native | 9000 | tcp://server:9000 | default/clickhouse |

**Container Names:**
- `pan-clickhouse`
- `pan-grafana`

**Volume Names:**
- `docker_clickhouse_data`
- `docker_grafana_data`

---

## Next Steps

1. ✅ Review dashboards
2. ✅ Change default passwords
3. ✅ Configure firewall
4. ✅ Set up auto-start (optional)
5. ✅ Configure backups (optional)
6. ✅ Set up HTTPS (optional)

---

**Support:** See `README.md` and `DASHBOARD_SUMMARY.md` for more information.

