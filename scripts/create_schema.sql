-- File Share Scan Schema for ClickHouse
-- Panzura Symphony scan data analysis

CREATE DATABASE IF NOT EXISTS file_share;

USE file_share;

CREATE TABLE IF NOT EXISTS file_scan (
    -- Raw fields from CSV
    path String,
    filename String,
    extension LowCardinality(String),
    size UInt64,
    migrated UInt8,
    creation_date DateTime,
    modify_date DateTime,
    last_accessed_date DateTime,
    owner String,
    acl String,
    duplicate_hash String,
    
    -- Metadata
    scan_date Date DEFAULT today(),
    
    -- Computed fields (ALIAS = computed on read, no storage cost)
    domain String ALIAS splitByChar('\\', owner)[1],
    username String ALIAS splitByChar('\\', owner)[2],
    days_since_modified UInt32 ALIAS dateDiff('day', modify_date, now()),
    days_since_accessed UInt32 ALIAS dateDiff('day', last_accessed_date, now()),
    file_age_days UInt32 ALIAS dateDiff('day', creation_date, now()),
    is_empty UInt8 ALIAS if(size = 0, 1, 0),
    is_directory UInt8 ALIAS if(filename = '.', 1, 0),
    path_depth UInt16 ALIAS length(splitByChar('/', path)) - 1
    
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(scan_date)
ORDER BY (scan_date, owner, modify_date, size)
SETTINGS index_granularity = 8192;

-- Create a view for easier querying with all computed fields visible
CREATE OR REPLACE VIEW file_scan_enriched AS
SELECT 
    path,
    filename,
    extension,
    size,
    migrated,
    creation_date,
    modify_date,
    last_accessed_date,
    owner,
    acl,
    duplicate_hash,
    scan_date,
    -- Computed fields explicitly selected
    splitByChar('\\', owner)[1] AS domain,
    splitByChar('\\', owner)[2] AS username,
    dateDiff('day', modify_date, now()) AS days_since_modified,
    dateDiff('day', last_accessed_date, now()) AS days_since_accessed,
    dateDiff('day', creation_date, now()) AS file_age_days,
    if(size = 0, 1, 0) AS is_empty,
    if(filename = '.', 1, 0) AS is_directory,
    length(splitByChar('/', path)) - 1 AS path_depth
FROM file_scan;

