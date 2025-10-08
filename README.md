# Pan-Kom: Panzura Symphony File Share Analytics

A Grafana dashboard system for analyzing Panzura Symphony file share scan data using ClickHouse.

## What It Does

Imports CSV file share scan data from Panzura Symphony into ClickHouse and provides 6 pre-built Grafana dashboards for visualization and analysis.

## Requirements

- macOS with Docker Desktop
- Python 3.13+
- Panzura Symphony CSV export file

## Quick Start

### 1. Setup Environment

```bash
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

### 2. Place CSV File

```bash
mv "your_scan_file.csv" data/symphony_scan.csv
```

### 3. Start Services

```bash
cd docker
docker compose up -d
```

### 4. Create Database Schema

```bash
cat scripts/create_schema.sql | docker exec -i pan-clickhouse clickhouse-client --password clickhouse
```

### 5. Import Data

```bash
source venv/bin/activate
python scripts/import_data.py
```

## Project Structure

```
pan-dashboard/
├── data/                         # CSV files (not in git)
├── docker/
│   ├── docker-compose.yml       # ClickHouse + Grafana services
│   └── grafana/provisioning/    # Dashboard definitions
├── scripts/
│   ├── create_schema.sql        # Database schema
│   └── import_data.py          # CSV importer
└── README.md
```

## Services

### ClickHouse
- **URL**: http://localhost:8123
- **Port**: 9000 (native)
- **Credentials**: username=`default`, password=`clickhouse`
- **Database**: `file_share`
- **Table**: `file_scan`

### Grafana
- **URL**: http://localhost:3000
- **Login**: admin/panzura
- **Dashboards**: Located in "File Share" folder

## Database Schema

The `file_scan` table contains:

**Raw Fields:**
- path, filename, extension
- size, migrated
- creation_date, modify_date, last_accessed_date
- owner, acl, duplicate_hash
- scan_date

**Computed Fields (ALIAS):**
- days_since_modified, days_since_accessed, file_age_days
- is_empty, is_directory
- path_depth

## Dashboards

Six pre-built dashboards are included:

1. **Executive Overview** - High-level metrics and top consumers
2. **Deep Dive - Data Explorer** - File distribution and characteristics
3. **File Aging & Stale Data Analysis** - Modification and access patterns
4. **Storage Optimization** - Empty files, recycle bin, duplicates
5. **User & Owner Analysis** - Ownership patterns and account analysis
6. **Security & Permissions** - Orphaned accounts and permission analysis

See `DASHBOARD_SUMMARY.md` for details on what each dashboard shows.

## Management Commands

### Stop Services
```bash
cd docker
docker compose down
```

### View Logs
```bash
docker compose logs clickhouse
docker compose logs grafana
```

### Connect to ClickHouse
```bash
docker exec -it pan-clickhouse clickhouse-client --password clickhouse
```

### Check Row Count
```bash
docker exec -i pan-clickhouse clickhouse-client --password clickhouse -q "SELECT COUNT(*) FROM file_share.file_scan"
```

## Troubleshooting

### ClickHouse Connection Issues
- Check containers are running: `docker compose ps`
- Restart if needed: `docker compose restart`

### Import Fails
- Verify CSV file location: `data/symphony_scan.csv`
- Check CSV format (Panzura Symphony with 4-line header)
- Ensure Python venv is activated
- Verify ClickHouse is accessible

### Performance Issues
- Increase batch size in `import_data.py` (default: 10,000)
- Check Docker Desktop resource allocation

## License

Internal use only.
