# Pan-Dashboard Deployment Status

**Date:** October 8, 2025  
**Server:** Ubuntu 25 Intel-based  
**Status:** ✅ FULLY OPERATIONAL

---

## Deployment Summary

Successfully deployed pan-dashboard on Ubuntu 25 server with macvlan networking.

### Architecture Changes from Mac Development

1. **Networking:** Migrated from bridge network to macvlan
2. **Storage:** Changed from Docker volumes to bind mounts
3. **Data Import:** Implemented containerized importer to work with macvlan

---

## Container Status

| Container | Status | IP Address | Health |
|-----------|--------|------------|--------|
| pan-clickhouse | Running | 192.168.33.223 | Healthy ✅ |
| pan-grafana | Running | 192.168.33.223 (shared) | Healthy ✅ |

**Network:** macvlan_net (external)

---

## Data Import Results

- **Total Rows Imported:** 25,525,845
- **Total Storage:** 42.35 TiB
- **Import Duration:** 167.26 seconds
- **Import Rate:** 152,610 rows/second
- **Errors:** 0
- **Status:** ✅ COMPLETE

---

## Services Verification

### ✅ ClickHouse Database
- Port: 8123 (HTTP), 9000 (native)
- Database: `file_share`
- Table: `file_scan`
- Row count: 25,525,845
- Queries: Working correctly
- Computed fields: Functional

### ✅ Grafana
- Port: 3000
- Version: 12.2.0
- Plugin: grafana-clickhouse-datasource v4.11.1
- Datasource: Configured and connected
- Dashboards: 6 provisioned

**Dashboard Files:**
1. executive-overview.json
2. data-explorer.json
3. file-aging.json
4. storage-optimization.json
5. user-owner-analysis.json
6. security-permissions.json

---

## Access Information

### From Network (not from Docker host due to macvlan)
- **Grafana:** http://192.168.33.223:3000
- **ClickHouse HTTP:** http://192.168.33.223:8123
- **ClickHouse Native:** tcp://192.168.33.223:9000

### Credentials
- **Grafana:** admin / panzura
- **ClickHouse:** default / clickhouse

---

## File Structure

```
/space/projects/pan-dashboard/
├── docker/
│   ├── compose.yaml                    # Main configuration
│   ├── data/
│   │   └── symphony_scan.csv          # 14GB CSV file
│   ├── clickhouse_data/               # ClickHouse storage (bind mount)
│   ├── grafana_data/                  # Grafana storage (bind mount)
│   └── grafana/provisioning/          # Auto-provisioned configs
├── scripts/
│   ├── create_schema.sql              # Database schema
│   ├── import_data.py                 # CSV importer
│   └── setup_environment.sh           # Environment setup
└── .gitignore                         # Excludes data directories

```

---

## Commands Reference

### Container Management
```bash
cd /space/projects/pan-dashboard/docker

# Start services
docker compose up -d

# Stop services
docker compose down

# View status
docker compose ps

# View logs
docker compose logs -f clickhouse
docker compose logs -f grafana
```

### Data Import (if needed)
```bash
cd /space/projects/pan-dashboard/docker

# Run importer
docker compose run --rm importer
```

### ClickHouse Queries
```bash
# Interactive client
docker exec -it pan-clickhouse clickhouse-client --password clickhouse

# Quick queries
docker exec pan-clickhouse clickhouse-client --password clickhouse --query "SELECT COUNT(*) FROM file_share.file_scan"
```

---

## Test Query Results

### Total Files and Size
```sql
SELECT COUNT(*) as total_files, formatReadableSize(SUM(size)) as total_size 
FROM file_share.file_scan
```
**Result:** 25,525,845 files | 42.35 TiB

### Top 5 Domains by File Count
```sql
SELECT splitByChar('\\', owner)[1] as domain, COUNT(*) as file_count 
FROM file_share.file_scan 
GROUP BY domain 
ORDER BY file_count DESC 
LIMIT 5
```
**Results:**
1. BUILTIN: 12,831,710
2. JGI: 8,273,804
3. S-1-5-21-671590300-1245243897-877285176-58802: 1,306,305
4. S-1-5-21-671590300-1245243897-877285176-1120: 460,937
5. S-1-5-21-671590300-1245243897-877285176-14149: 184,231

---

## Key Configuration Details

### Macvlan Network
- **Network Name:** macvlan_net
- **Driver:** macvlan
- **Subnet:** 192.168.33.0/24
- **Gateway:** 192.168.33.1
- **Parent Interface:** br33
- **Container IP:** 192.168.33.223

### Network Topology
- ClickHouse has macvlan IP (192.168.33.223)
- Grafana shares ClickHouse's network namespace via `network_mode: service:clickhouse`
- Importer (when running) shares ClickHouse's network for connectivity

### Bind Mounts
All data is stored on host filesystem:
- `/space/projects/pan-dashboard/docker/clickhouse_data` → `/var/lib/clickhouse`
- `/space/projects/pan-dashboard/docker/grafana_data` → `/var/lib/grafana`
- `/space/projects/pan-dashboard/docker/data` → `/data` (in importer)

---

## Issues Resolved

### 1. Grafana Permission Error ✅ FIXED
**Problem:** Grafana couldn't write to `/var/lib/grafana`  
**Cause:** Bind mount directory owned by root, Grafana runs as UID 472  
**Solution:** Changed ownership: `chown -R 472:472 docker/grafana_data`

### 2. Host Cannot Access Macvlan Containers ✅ EXPECTED BEHAVIOR
**Problem:** Cannot curl http://192.168.33.223:3000 from Docker host  
**Cause:** Macvlan limitation - host cannot communicate directly with macvlan containers  
**Solution:** Access from other network devices, or use `docker exec` for testing

### 3. Data Import with Macvlan ✅ SOLVED
**Problem:** Python script on host can't reach ClickHouse at localhost  
**Cause:** ClickHouse is on macvlan network, not accessible from host  
**Solution:** Created importer container that shares ClickHouse's network namespace

---

## Performance Notes

- Import performance: 152K rows/second on Intel Ubuntu server
- ClickHouse running smoothly with 25.5M rows
- Grafana responsive and healthy
- All health checks passing

---

## Next Steps

1. Access Grafana from network device: http://192.168.33.223:3000
2. Login with admin/panzura
3. Navigate to "File Share" folder
4. Explore the 6 pre-built dashboards
5. Data is ready for analysis!

---

## Backup Considerations

**Important directories to backup:**
- `/space/projects/pan-dashboard/docker/clickhouse_data/` - Database
- `/space/projects/pan-dashboard/docker/grafana_data/` - Grafana settings
- `/space/projects/pan-dashboard/docker/data/symphony_scan.csv` - Source data

**Configuration files (in git):**
- `docker/compose.yaml`
- `docker/grafana/provisioning/`
- `scripts/`

---

**Deployment completed successfully! All systems operational.** ✅

