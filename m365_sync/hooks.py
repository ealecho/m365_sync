app_name = "m365_sync"
app_title = "M365 Sync"
app_publisher = "Your Company"
app_description = "Sync Microsoft 365 groups to ERPNext roles"
app_email = "dev@yourcompany.com"
app_license = "MIT"

fixtures = []

scheduler_events = {
    "hourly": [
        "m365_sync.m365_sync.tasks.sync_hourly_mappings"
    ],
    "daily": [
        "m365_sync.m365_sync.tasks.sync_daily_mappings"
    ]
}

doc_events = {
    "User": {
        "after_insert": "m365_sync.m365_sync.events.sync_new_user_roles"
    }
}
