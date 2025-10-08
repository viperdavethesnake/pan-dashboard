#!/usr/bin/env python3
"""
Import Panzura Symphony file share scan data into ClickHouse
Handles large CSV files efficiently with batch processing
"""

import csv
import sys
from datetime import datetime
import clickhouse_connect

# Configuration
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 8123  # HTTP port for clickhouse-connect
DATABASE = 'file_share'
TABLE = 'file_scan'
CSV_FILE = '/data/symphony_scan.csv'
BATCH_SIZE = 10000  # Insert in batches for better performance

def parse_boolean(value):
    """Convert string boolean to integer (0/1)"""
    return 1 if value.lower() == 'true' else 0

def parse_datetime(value):
    """Parse ISO datetime string to datetime object"""
    if not value:
        return datetime(1970, 1, 1)  # Default for empty dates
    try:
        # Remove 'Z' and parse
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except:
        return datetime(1970, 1, 1)

def parse_size(value):
    """Parse size as integer"""
    try:
        return int(value) if value else 0
    except:
        return 0

def import_data():
    """Import CSV data into ClickHouse"""
    
    print(f"Connecting to ClickHouse at {CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}...")
    client = clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, username='default', password='clickhouse')
    
    print(f"Opening CSV file: {CSV_FILE}")
    
    batch = []
    total_rows = 0
    skipped_rows = 0
    start_time = datetime.now()
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        # Skip the first 3 lines (Source, Policy, URI, blank line)
        for _ in range(4):
            next(f)
        
        # Line 4 contains the actual CSV header, line 5+ contains data
        reader = csv.DictReader(f, fieldnames=['Path', 'Filename', 'Extension', 'Size', 'Migrated', 
                                                 'Creation Date', 'Modify Date', 'Last Accessed Date', 
                                                 'Owner', 'ACL', 'Possible Duplicate Metadata Hash'])
        
        print("Starting import...")
        
        for row_num, row in enumerate(reader, 1):
            try:
                # Parse and prepare data
                record = (
                    row['Path'].strip('"'),
                    row['Filename'].strip('"'),
                    row['Extension'].strip('"'),
                    parse_size(row['Size']),
                    parse_boolean(row['Migrated']),
                    parse_datetime(row['Creation Date']),
                    parse_datetime(row['Modify Date']),
                    parse_datetime(row['Last Accessed Date']),
                    row['Owner'].strip('"'),
                    row['ACL'].strip('"'),
                    row.get('Possible Duplicate Metadata Hash', '').strip('"')
                )
                
                batch.append(record)
                
                # Insert batch when full
                if len(batch) >= BATCH_SIZE:
                    client.insert(
                        f'{DATABASE}.{TABLE}',
                        batch,
                        column_names=['path', 'filename', 'extension', 'size', 'migrated',
                                     'creation_date', 'modify_date', 'last_accessed_date',
                                     'owner', 'acl', 'duplicate_hash']
                    )
                    total_rows += len(batch)
                    batch = []
                    
                    # Progress update
                    if total_rows % 100000 == 0:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        rate = total_rows / elapsed if elapsed > 0 else 0
                        print(f"Imported {total_rows:,} rows ({rate:.0f} rows/sec)")
                
            except Exception as e:
                skipped_rows += 1
                if skipped_rows <= 10:  # Only print first 10 errors
                    print(f"Error on row {row_num}: {e}")
                continue
        
        # Insert remaining batch
        if batch:
            client.insert(
                f'{DATABASE}.{TABLE}',
                batch,
                column_names=['path', 'filename', 'extension', 'size', 'migrated',
                             'creation_date', 'modify_date', 'last_accessed_date',
                             'owner', 'acl', 'duplicate_hash']
            )
            total_rows += len(batch)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("Import Complete!")
    print("="*60)
    print(f"Total rows imported: {total_rows:,}")
    print(f"Rows skipped (errors): {skipped_rows:,}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Average rate: {total_rows/duration:.0f} rows/second")
    print("="*60)
    
    # Verify data
    result = client.query(f'SELECT COUNT(*) FROM {DATABASE}.{TABLE}')
    count = result.result_rows[0][0]
    print(f"\nVerification: {count:,} rows in database")
    
    client.close()

if __name__ == '__main__':
    try:
        import_data()
    except KeyboardInterrupt:
        print("\n\nImport interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)

