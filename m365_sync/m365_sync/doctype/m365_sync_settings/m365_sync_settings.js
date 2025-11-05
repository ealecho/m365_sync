frappe.ui.form.on('M365 Sync Settings', {
	refresh: function(frm) {
		if (frm.doc.enabled) {
			frm.add_custom_button(__('Test Connection'), function() {
				frappe.call({
					method: 'm365_sync.m365_sync.api.test_connection',
					callback: function(r) {
						if (r.message && r.message.status === 'success') {
							frappe.msgprint(__('Connection successful!'));
						} else {
							frappe.msgprint(__('Connection failed. Check error log.'));
						}
					}
				});
			});

			frm.add_custom_button(__('Sync All Now'), function() {
				frappe.call({
					method: 'm365_sync.m365_sync.doctype.m365_group_role_mapping.m365_group_role_mapping.sync_all_mappings',
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__('Synced {0} mappings', [r.message.synced]));
							frm.reload_doc();
						}
					}
				});
			});
		}
	}
});
