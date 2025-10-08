# AI Context Document - Pan-Dashboard Project

**Last Updated:** October 8, 2025  
**Project Status:** Published to GitHub at v1.0.0  
**Current Phase:** Preparing for Linux server deployment  
**Next Task:** Clone and deploy on Ubuntu 25 server with macvlan networking

---

## Project Overview

**Pan-Dashboard** is a complete Grafana + ClickHouse analytics solution for visualizing Panzura Symphony file share scan data.

- **GitHub Repo:** https://github.com/viperdavethesnake/pan-dashboard
- **Version:** v1.0.0 (tagged and released)
- **Development:** Completed on macOS 15 (M4 MacBook Pro)
- **Next Step:** Deploy to Ubuntu 25 Linux server

### What This Does
- Imports large CSV files (24M+ rows) from Panzura Symphony file share scans into ClickHouse
- Provides 6 pre-built Grafana dashboards for storage optimization, security analysis, and file aging
- Runs entirely in Docker containers (ClickHouse + Grafana)
- Python import script with batch processing for efficient data loading

---

## Current Status

### ✅ Completed on Mac
- [x] Docker containers configured and tested (`pan-clickhouse`, `pan-grafana`)
- [x] ClickHouse schema created (`file_share.file_scan` table)
- [x] Python import script working (24M rows in ~2-3 minutes)
- [x] All 6 Grafana dashboards functional
- [x] Complete documentation (README, GETTING_STARTED, DASHBOARD_SUMMARY)
- [x] Published to GitHub with v1.0.0 tag
- [x] .gitignore configured (CSV files excluded)

### 🔄 Next: Linux Server Deployment

**Target Environment:**
- **OS:** Ubuntu 25
- **Docker:** Already installed
- **Networking:** Will use macvlan (details to be provided by user)
- **Data:** CSV file needs to be transferred separately (not in git, too large)

---

## Linux Deployment Plan

### Step 1: Clone Repository
```bash
cd /desired/path
git clone https://github.com/viperdavethesnake/pan-dashboard.git
cd pan-dashboard
```

### Step 2: Transfer CSV Data
- CSV file is gitignored (~13GB, 24M+ rows)
- Must be transferred separately to server: `data/symphony_scan.csv`
- Use rsync, scp, or similar
- File format: Panzura Symphony scan export (4-line header)

### Step 3: Configure Macvlan Networking
- User will provide specific macvlan configuration details
- Will need to modify `docker/docker-compose.yml`
- Current setup uses default bridge network (`pan-network`)

### Step 4: Setup Python Environment
```bash
./scripts/setup_environment.sh
source venv/bin/activate
```

### Step 5: Start Containers
```bash
cd docker
docker compose up -d
```

### Step 6: Create Database Schema
```bash
cat scripts/create_schema.sql | docker exec -i pan-clickhouse clickhouse-client --password clickhouse
```

### Step 7: Import Data
```bash
source venv/bin/activate
python scripts/import_data.py
```

### Step 8: Access Grafana
- Default: http://localhost:3000
- With macvlan: http://[assigned-IP]:3000
- Login: admin / panzura

---

## Critical Technical Details

### Docker Setup
- **Containers:** `pan-clickhouse` and `pan-grafana`
- **Current Network:** `pan-network` (bridge) - will change to macvlan
- **Ports:**
  - Grafana: 3000 (web UI)
  - ClickHouse: 8123 (HTTP), 9000 (native)
- **Volumes:**
  - `docker_clickhouse_data` - Database storage
  - `docker_grafana_data` - Grafana settings

### Authentication
- **Grafana:** admin / panzura
- **ClickHouse:** default / clickhouse

### Database
- **Database name:** `file_share`
- **Table name:** `file_scan`
- **Important:** Never reference `file_scan_enriched` (doesn't exist)
- Use computed expressions, not ALIAS column references in queries

### CSV File Details
- **Location:** `data/symphony_scan.csv` (gitignored)
- **Source:** Panzura Symphony file share scan export
- **Format:** 4-line header (Source, Policy, URI, blank line) then CSV data
- **Typical Size:** ~13GB, 24M+ rows
- **Owner Format:** `DOMAIN\username`

### Grafana Dashboards
- **Plugin:** grafana-clickhouse-datasource v4.11.1
- **Auto-provisioned:** All 6 dashboards load automatically
- **Folder:** "File Share" (in Grafana UI)
- **Known Limitation:** Plugin doesn't handle raw table data well - all dashboards use aggregate visualizations

---

## Key Differences: Mac → Linux

### What's the Same
- Docker Compose configuration
- Python scripts and dependencies
- Database schema
- Grafana dashboards
- All code and configs

### What's Different
- **Networking:** Adding macvlan configuration (user will provide details)
- **File paths:** Should work the same (both Unix-based)
- **Python:** Uses system Python 3.x (Mac has 3.13, Ubuntu will have 3.x)
- **Docker:** Linux native Docker (vs Docker Desktop on Mac)

### What Won't Transfer
- **Docker volumes:** Cannot copy volumes from Mac to Linux
- **Must re-import data:** Takes 2-3 minutes for 24M rows
- **CSV file:** Must transfer separately (gitignored)

---

## Macvlan Networking (To Be Configured)

### What We Know
- User wants to use macvlan for container networking
- This will assign containers their own IP addresses on the network
- Will need to modify `docker-compose.yml`

### What We Need From User
- Network interface name (e.g., `eth0`, `ens18`)
- Subnet and gateway
- IP addresses for containers (or DHCP)
- Parent network interface

### Example Macvlan Config (Template)
```yaml
networks:
  pan-network:
    driver: macvlan
    driver_opts:
      parent: eth0  # User will provide
    ipam:
      config:
        - subnet: 192.168.1.0/24     # User will provide
          gateway: 192.168.1.1        # User will provide
```

Then assign static IPs to services or use DHCP.

---

## User Preferences (CRITICAL - MUST FOLLOW)

These preferences MUST be followed:

1. **No commands without permission** - Always ask before executing terminal commands
2. **No changes without agreement** - Discuss changes and options before implementing
3. **Simple Python code** - Use bare essentials, no frills or complexity
4. **No mock/placeholder data** - Code examples should use real data or no data
5. **Factual documentation only** - No analytics, suggestions, or action plans in docs
6. **Symphony admin group** - Should never own or have permissions on shared folders (data quality note)

### Exception
- Read-only operations (file reads, grep, codebase search) are allowed without asking

---

## Project Structure

```
pan-dashboard/
├── data/
│   ├── .gitkeep                   # In git
│   └── symphony_scan.csv          # NOT in git (must transfer separately)
├── docker/
│   ├── docker-compose.yml         # Will modify for macvlan
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── clickhouse.yml # Auto-configured datasource
│           └── dashboards/
│               ├── dashboard.yml  # Dashboard provisioning
│               └── json/          # 6 dashboard JSON files
├── scripts/
│   ├── create_schema.sql          # Database schema
│   ├── import_data.py             # CSV importer
│   └── setup_environment.sh       # Environment setup
├── venv/                          # Python virtual environment (gitignored)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git exclusions
├── .cursorrules                   # Cursor AI rules (important!)
├── README.md                      # Main documentation
├── GETTING_STARTED.md             # Linux deployment guide
├── DASHBOARD_SUMMARY.md           # Dashboard overview
└── AI_CONTEXT.md                  # This file
```

---

## Known Issues & Solutions

### 1. Grafana ClickHouse Plugin Limitations
- **Problem:** Plugin expects time-series data, fails on raw tables
- **Solution:** Use only aggregate visualizations (stats, bar charts)
- **Never:** Use raw table panels or pie charts

### 2. ALIAS Column References
- **Problem:** Queries fail when referencing computed ALIAS columns
- **Solution:** Use full SQL expression instead

### 3. Owner Field Parsing
- **Format:** `DOMAIN\username`
- **Domain extraction:** `splitByChar('\\\\', owner)[1]`
- **Username extraction:** `splitByChar('\\\\', owner)[2]`
- **Note:** Double backslash escaping required in SQL

### 4. Large CSV Files
- **Problem:** Git not suitable for large CSV files (13GB+)
- **Solution:** Transfer separately (rsync, scp, etc.)
- **Import Time:** 2-3 minutes per 24M rows

---

## Quick Commands Reference

### Container Management
```bash
# Start containers
cd docker && docker compose up -d

# Stop containers
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart pan-grafana
docker compose restart pan-clickhouse
```

### Data Management
```bash
# Create schema
cat scripts/create_schema.sql | docker exec -i pan-clickhouse clickhouse-client --password clickhouse

# Import data
source venv/bin/activate
python scripts/import_data.py

# Check row count
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT COUNT(*) FROM file_share.file_scan"

# Interactive ClickHouse client
docker exec -it pan-clickhouse clickhouse-client --password clickhouse
```

### Troubleshooting
```bash
# Check container status
docker ps -a

# Check container logs
docker logs pan-clickhouse
docker logs pan-grafana

# Check network
docker network ls
docker network inspect pan-network

# Verify volumes
docker volume ls
docker volume inspect docker_clickhouse_data
```

---

## Access Points

### Current (Default Bridge Network)
- **Grafana:** http://localhost:3000
- **ClickHouse HTTP:** http://localhost:8123
- **ClickHouse Native:** tcp://localhost:9000

### After Macvlan Configuration
- Will use assigned IP addresses
- User will provide specifics

---

## Important Files in Repository

### Must Read Before Changes
- `.cursorrules` - Project rules and user preferences
- `GETTING_STARTED.md` - Complete deployment guide
- `docker/docker-compose.yml` - Container configuration

### Key Scripts
- `scripts/setup_environment.sh` - Python environment setup
- `scripts/import_data.py` - CSV import with progress tracking
- `scripts/create_schema.sql` - Database table definition

### Documentation
- `README.md` - Project overview
- `DASHBOARD_SUMMARY.md` - Dashboard descriptions
- `GETTING_STARTED.md` - Deployment instructions

---

## Testing Validation

### On Mac (Completed)
- ✅ 24,257,739 rows imported successfully
- ✅ All 6 dashboards displaying data correctly
- ✅ All queries returning results
- ✅ Containers stable and performant

### On Linux (To Validate)
- [ ] Containers start successfully with macvlan
- [ ] ClickHouse accessible via network IP
- [ ] Grafana accessible via network IP
- [ ] Data import completes successfully
- [ ] All dashboards work correctly
- [ ] Network connectivity from other systems

---

## Workflow for Linux Deployment

### When User Provides Macvlan Details
1. Confirm network interface, subnet, gateway, IPs
2. Show proposed `docker-compose.yml` changes
3. Discuss any implications or alternatives
4. Wait for approval
5. Make changes
6. Test and validate

### When Running Commands on Server
1. Show command you'll run
2. Explain what it does
3. Ask permission (unless read-only)
4. Execute only after approval
5. Report results

### When Issues Arise
1. Identify the problem
2. Check logs and status
3. Explain root cause
4. Propose solution(s)
5. Discuss before implementing

---

## Summary for New AI Agent

**What you need to know:**
- Project is complete and published to GitHub at v1.0.0
- Developed and tested on macOS, now deploying to Ubuntu 25 Linux server
- Docker already installed on server
- User will configure macvlan networking (details coming)
- CSV data must be transferred separately (not in git)
- All code is tested and functional
- User has specific preferences about permissions and changes

**What to do:**
1. Wait for user to resume on Linux server
2. Get macvlan networking details from user
3. Help configure docker-compose.yml for macvlan
4. Guide through deployment steps
5. Validate everything works on Linux

**What NOT to do:**
- Don't run commands without explicit permission
- Don't add mock/placeholder data
- Don't add analytics or suggestions to documentation
- Don't commit CSV files (they're gitignored)
- Don't change anything without discussion
- Don't skip reading `.cursorrules` - it has critical project rules

**User Preferences (from memories):**
- Always ask before running commands/scripts
- Discuss before adding or changing code
- Simple Python code, no complexity
- No mock data in examples
- Symphony admin group should never own shared folders

**Ready for deployment!** The project is solid and ready to run on Linux with macvlan networking.

---

## Contact & Support

- **User:** microbarley (viperdavethesnake on GitHub)
- **Dev Path:** `/Users/microbarley/visualstudio/pan-dashboard` (Mac)
- **Server Path:** TBD (will be provided on Linux server)
- **Platform:** macOS 15 → Ubuntu 25 Linux

---

**Good luck with the Linux deployment!** Everything is ready to go once the server details are provided.




