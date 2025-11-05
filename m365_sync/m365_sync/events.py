import frappe

def sync_new_user_roles(doc, method):
	settings = frappe.get_single("M365 Sync Settings")
	
	if not settings.enabled or not settings.sync_on_login:
		return
	
	try:
		from m365_sync.m365_sync.api import get_m365_client
		
		client = get_m365_client()
		
		mappings = frappe.get_all(
			"M365 Group Role Mapping",
			filters={"enabled": 1},
			fields=["name", "m365_group_id", "erpnext_role"]
		)
		
		for mapping in mappings:
			members = client.get_group_members(mapping.m365_group_id)
			
			for member in members:
				if member.get("email") == doc.email:
					if not any(r.role == mapping.erpnext_role for r in doc.roles):
						doc.append("roles", {"role": mapping.erpnext_role})
		
		if doc.flags.roles_updated:
			doc.save(ignore_permissions=True)
			
	except Exception as e:
		frappe.log_error(f"Error syncing roles for new user {doc.email}: {str(e)}", "M365 Sync")
