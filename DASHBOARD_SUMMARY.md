# Dashboard Summary

**Data Source**: Panzura Symphony File Share Scan  
**Location**: DA2-PFPS01 E Drive  
**Scan Date**: September 24, 2025

---

## Data Overview

- **Total Files**: 24.3 million
- **Total Storage**: 42.35 TiB
- **Total Directories**: 1,268,106
- **Average File Size**: 1.83 MiB

---

## Dashboard Descriptions

### 1. Executive Overview - File Share Analytics

**Purpose**: High-level metrics and summary statistics.

**Panels**:
- Total Files: 24 million
- Total Storage Used: 42.35 TiB
- Total Directories: 1.3 million
- Average File Size: 1.83 MiB
- Top 10 Owners by Storage (horizontal bar chart)
- File Count by Extension Top 15 (horizontal bar chart)
- Top 10 Space Consumers by User (horizontal bar chart)
- Storage by File Type Top 10 (horizontal bar chart)

**What You See**:
- BUILTIN\Administrators: 21.2 TiB
- JGI\dweeks: 1.28 TiB
- JGI\StSmith: 1.00 TiB
- Various file extensions (JPG, ZIP, MPG, CR2, MTS, L2L, etc.)

---

### 2. Deep Dive - Data Explorer

**Purpose**: Detailed file distribution analysis.

**Panels**:
- Total Files: 24 million
- Total Storage: 42.35 TiB
- Average File Size: 1.83 MiB
- Files Over 1GB: 4K
- Files Over 100MB: 36K files
- Storage Over 100MB: Large portion of total
- Files Not Modified in 2+ Years: 23.6M files
- Storage Not Modified in 2+ Years: 39.8 TiB
- Top 15 File Extensions by count (horizontal bar chart)
- Top 15 Users by File Count (horizontal bar chart)
- Top 15 Extensions by Storage Size (horizontal bar chart)
- Top 15 Users by Storage Size (horizontal bar chart)
- File Age Distribution by Count (horizontal bar chart)
- File Age Distribution by Storage (horizontal bar chart)

**File Age Breakdown**:
- 2+ years: 23.6M files / 39.8 TiB
- 1-2 years: 327K files / 1.13 TiB
- 6-12 months: 171K files / 743 GiB
- 3-6 months: 93K files / 407 GiB
- 1-3 months: 39K files / 180 GiB
- < 1 month: 8.5K files / 95.7 GiB

---

### 3. File Aging & Stale Data Analysis

**Purpose**: File modification and access patterns.

**Panels**:
- Files Not Modified in 1+ Year: 23.9M files
- Storage in 1+ Year Old Files: 40.9 TiB
- Files Not Modified in 2+ Years: 23.6M files
- Storage in 2+ Year Old Files: 39.8 TiB
- File Count by Modification Age (horizontal bar chart showing 7 age groups)
- Storage Size by Modification Age (horizontal bar chart)
- Files Not Accessed in Over 1 Year by Extension (horizontal bar chart)

**Age Groups**:
- 0-30 days
- 30-90 days
- 90-180 days
- 6-12 months
- 1-2 years
- 2-3 years
- 3+ years

---

### 4. Storage Optimization

**Purpose**: Identify storage usage patterns.

**Panels**:
- Empty/Zero-Byte Files: 384K
- Recycle Bin Files: 3K
- Recycle Bin Storage: 3.06 GiB
- Potential Duplicates: 3 million
- Storage by File Size Category (horizontal bar chart)

**File Size Categories**:
- Empty (0 bytes)
- < 1 KB
- 1 KB - 1 MB
- 1 MB - 10 MB
- 10 MB - 100 MB
- 100 MB - 1 GB
- > 1 GB

**What You See**:
- Files > 1GB: 13.4M files consuming 13.6 TiB
- 100MB-1GB: 146K files consuming 9.08 TiB
- 10MB-100MB: 1.07M files consuming 10.7 TiB
- Smaller files represent minimal storage

---

### 5. User & Owner Analysis

**Purpose**: Ownership patterns and account information.

**Panels**:
- Total Unique Users: 1K
- Admin-Owned Files: 21K
- Admin-Owned Storage: 234.89 GiB
- Total Unique Owners: 610
- Top 15 Owners/Accounts by File Count (horizontal bar chart)
- Storage Distribution by Top 10 Users (horizontal bar chart)

**Top Owners by File Count**:
- BUILTIN\Administrators: 12.2M files
- Orphaned SID accounts: 4.2M files (multiple SIDs)
- JGI\dweeks: 1.07M files
- JGI\StSmith: 446K files
- JGI\Domain Admins: 401K files

**Top Owners by Storage**:
- BUILTIN\Administrators: 21.2 TiB
- JGI\dweeks: 1.28 TiB
- JGI\StSmith: 1.00 TiB
- Various orphaned SID accounts

---

### 6. Security & Permissions Analysis

**Purpose**: Security and permission information.

**Panels**:
- Files with Unknown/Everyone Permissions: 0
- Files with SID-Only Owners: 4 million
- Storage by Orphaned Accounts: 3.31 TiB
- Total Unique ACL Patterns: 4K
- Files by Owner Type (horizontal bar chart)
- Storage by Owner Type (horizontal bar chart)

**Owner Type Breakdown (by file count)**:
- System (BUILTIN): 12.2M files
- Regular User: 7.6M files
- Orphaned (SID): 4.2M files
- System (NT AUTHORITY): Small percentage

**Owner Type Breakdown (by storage)**:
- System (BUILTIN): 21.4 TiB
- Regular User: 16.8 TiB
- Orphaned (SID): 3.31 TiB
- NT AUTHORITY: 461 GiB

---

## Accessing Dashboards

1. Open browser to: http://localhost:3000
2. Login: admin/panzura
3. Navigate to: Dashboards → File Share folder
4. Select dashboard to view

All dashboards auto-refresh every 5 minutes.

---

**Document Version**: 1.0  
**Last Updated**: October 8, 2025
