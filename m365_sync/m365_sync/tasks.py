import frappe

def sync_hourly_mappings():
	mappings = frappe.get_all(
		"M365 Group Role Mapping",
		filters={
			"enabled": 1,
			"auto_sync": 1,
			"sync_frequency": "Hourly"
		},
		pluck="name"
	)
	
	for mapping_name in mappings:
		frappe.enqueue(
			"m365_sync.m365_sync.doctype.m365_group_role_mapping.m365_group_role_mapping.sync_now",
			queue='default',
			timeout=300,
			mapping_name=mapping_name
		)

def sync_daily_mappings():
	mappings = frappe.get_all(
		"M365 Group Role Mapping",
		filters={
			"enabled": 1,
			"auto_sync": 1,
			"sync_frequency": ["in", ["Daily", "Weekly"]]
		},
		pluck="name"
	)
	
	for mapping_name in mappings:
		frappe.enqueue(
			"m365_sync.m365_sync.doctype.m365_group_role_mapping.m365_group_role_mapping.sync_now",
			queue='default',
			timeout=300,
			mapping_name=mapping_name
		)
