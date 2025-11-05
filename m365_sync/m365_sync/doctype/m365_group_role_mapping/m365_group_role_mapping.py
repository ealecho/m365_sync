import frappe
from frappe.model.document import Document
from frappe import _

class M365GroupRoleMapping(Document):
	def validate(self):
		if not frappe.db.exists("Role", self.erpnext_role):
			frappe.throw(_("Role {0} does not exist").format(self.erpnext_role))
		
		if not self.m365_group_id:
			frappe.throw(_("M365 Group ID is required"))
	
	def on_update(self):
		if self.enabled and self.auto_sync:
			frappe.enqueue(
				self.sync_group_members,
				queue='default',
				timeout=300
			)
	
	def sync_group_members(self):
		try:
			from m365_sync.m365_sync.api import get_m365_client
			
			client = get_m365_client()
			members = client.get_group_members(self.m365_group_id)
			
			if not members:
				self.db_set("sync_status", "No members found in M365 group")
				return
			
			synced_count = 0
			errors = []
			
			for member in members:
				try:
					self.assign_role_to_user(member.get("email"), self.erpnext_role)
					synced_count += 1
				except Exception as e:
					errors.append(f"{member.get('email')}: {str(e)}")
			
			self.db_set("last_sync", frappe.utils.now())
			self.db_set("members_synced", synced_count)
			
			status_msg = f"Synced {synced_count} members"
			if errors:
				status_msg += f"\nErrors: {', '.join(errors[:5])}"
			self.db_set("sync_status", status_msg)
			
			frappe.db.commit()
			
		except Exception as e:
			frappe.log_error(f"M365 Sync Error: {str(e)}", "M365 Group Sync")
			self.db_set("sync_status", f"Error: {str(e)}")
	
	def assign_role_to_user(self, email, role):
		if not frappe.db.exists("User", email):
			frappe.log_error(f"User {email} does not exist in ERPNext", "M365 Sync")
			return
		
		user = frappe.get_doc("User", email)
		
		if not any(r.role == role for r in user.roles):
			user.append("roles", {"role": role})
			user.save(ignore_permissions=True)
			frappe.db.commit()

@frappe.whitelist()
def sync_now(mapping_name):
	mapping = frappe.get_doc("M365 Group Role Mapping", mapping_name)
	frappe.enqueue(
		mapping.sync_group_members,
		queue='default',
		timeout=300
	)
	return {"status": "success", "message": "Sync queued"}

@frappe.whitelist()
def sync_all_mappings():
	mappings = frappe.get_all(
		"M365 Group Role Mapping",
		filters={"enabled": 1},
		pluck="name"
	)
	
	for mapping_name in mappings:
		mapping = frappe.get_doc("M365 Group Role Mapping", mapping_name)
		mapping.sync_group_members()
	
	return {"status": "success", "synced": len(mappings)}
