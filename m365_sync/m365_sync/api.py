import frappe
from frappe import _
import requests

class M365Client:
	def __init__(self):
		self.base_url = "https://graph.microsoft.com/v1.0"
		self.access_token = None
		self._authenticate()
	
	def _authenticate(self):
		settings = frappe.get_single("M365 Sync Settings")
		
		if not settings or not settings.enabled:
			frappe.throw(_("M365 Sync is not configured or enabled"))
		
		tenant_id = settings.tenant_id
		client_id = settings.get_password("client_id")
		client_secret = settings.get_password("client_secret")
		
		if not all([tenant_id, client_id, client_secret]):
			frappe.throw(_("M365 credentials are incomplete"))
		
		token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
		
		data = {
			"client_id": client_id,
			"client_secret": client_secret,
			"scope": "https://graph.microsoft.com/.default",
			"grant_type": "client_credentials"
		}
		
		try:
			response = requests.post(token_url, data=data, timeout=30)
			response.raise_for_status()
			self.access_token = response.json().get("access_token")
		except requests.exceptions.RequestException as e:
			frappe.log_error(f"Failed to authenticate with M365: {str(e)}", "M365 Auth Error")
			frappe.throw(_("Failed to authenticate with Microsoft 365"))
	
	def get(self, endpoint):
		headers = {
			"Authorization": f"Bearer {self.access_token}",
			"Content-Type": "application/json"
		}
		
		url = f"{self.base_url}{endpoint}"
		
		try:
			response = requests.get(url, headers=headers, timeout=30)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.RequestException as e:
			frappe.log_error(f"M365 API request failed: {str(e)}", "M365 API Error")
			frappe.throw(_("Failed to fetch data from Microsoft 365"))
	
	def get_group_members(self, group_id):
		result = self.get(f"/groups/{group_id}/members")
		
		members = []
		for member in result.get("value", []):
			if member.get("mail"):
				members.append({
					"email": member.get("mail"),
					"name": member.get("displayName"),
					"id": member.get("id")
				})
		
		return members
	
	def get_groups(self, search_term=None):
		endpoint = "/groups"
		if search_term:
			endpoint += f"?$filter=startswith(displayName,'{search_term}')"
		
		result = self.get(endpoint)
		
		groups = []
		for group in result.get("value", []):
			groups.append({
				"id": group.get("id"),
				"name": group.get("displayName"),
				"description": group.get("description")
			})
		
		return groups

def get_m365_client():
	return M365Client()

@frappe.whitelist()
def test_connection():
	try:
		client = get_m365_client()
		client.get("/organization")
		
		settings = frappe.get_single("M365 Sync Settings")
		settings.db_set("sync_log", f"Connection test successful at {frappe.utils.now()}")
		
		return {"status": "success", "message": "Connection successful"}
	except Exception as e:
		frappe.log_error(f"Connection test failed: {str(e)}", "M365 Connection Test")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_m365_groups(search_term=None):
	try:
		client = get_m365_client()
		groups = client.get_groups(search_term)
		return groups
	except Exception as e:
		frappe.log_error(f"Failed to fetch M365 groups: {str(e)}", "M365 API Error")
		frappe.throw(_("Failed to fetch M365 groups"))
