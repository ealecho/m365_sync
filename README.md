# M365 Sync

Sync Microsoft 365 groups to ERPNext roles.

## Features

- Map M365 groups to ERPNext roles
- Automatic synchronization of group members
- Scheduled sync tasks (hourly/daily/weekly)
- Manual sync triggers
- Comprehensive sync status tracking

## Installation

```bash
bench get-app /path/to/m365_sync
bench --site your-site-name install-app m365_sync
```

## Configuration

1. Go to **M365 Sync Settings**
2. Enable the integration
3. Enter your Microsoft 365 credentials:
   - Tenant ID
   - Client ID
   - Client Secret

## Usage

1. Create **M365 Group Role Mapping** documents
2. Map M365 Group IDs to ERPNext Roles
3. Enable auto-sync or manually trigger synchronization

## Requirements

- ERPNext v15
- Microsoft 365 tenant with admin access
- Azure AD app registration with appropriate permissions
