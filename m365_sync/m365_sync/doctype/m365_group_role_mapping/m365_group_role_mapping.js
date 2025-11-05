frappe.ui.form.on('M365 Group Role Mapping', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Sync Now'), function() {
				frappe.call({
					method: 'm365_sync.m365_sync.doctype.m365_group_role_mapping.m365_group_role_mapping.sync_now',
					args: {
						mapping_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === 'success') {
							frappe.msgprint(__('Sync started. Check sync status in a moment.'));
							setTimeout(function() {
								frm.reload_doc();
							}, 3000);
						}
					}
				});
			});

			frm.add_custom_button(__('Get M365 Groups'), function() {
				frappe.call({
					method: 'm365_sync.m365_sync.api.get_m365_groups',
					callback: function(r) {
						if (r.message) {
							let d = new frappe.ui.Dialog({
								title: __('Select M365 Group'),
								fields: [
									{
										fieldtype: 'HTML',
										fieldname: 'groups_html'
									}
								]
							});

							let html = '<div style="max-height: 400px; overflow-y: auto;">';
							r.message.forEach(function(group) {
								html += `<div style="padding: 10px; border-bottom: 1px solid #d1d8dd; cursor: pointer;" 
									onclick="cur_frm.set_value('m365_group_id', '${group.id}'); 
									cur_frm.set_value('m365_group_name', '${group.name}'); 
									cur_dialog.hide();">
									<strong>${group.name}</strong><br>
									<small>${group.description || 'No description'}</small><br>
									<small style="color: #888;">ID: ${group.id}</small>
								</div>`;
							});
							html += '</div>';

							d.fields_dict.groups_html.$wrapper.html(html);
							d.show();
						}
					}
				});
			});
		}
	}
});
