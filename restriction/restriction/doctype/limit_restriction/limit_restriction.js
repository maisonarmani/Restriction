// Copyright (c) 2016, bobzz.zone@gmail.com and masonarmani38@gmail.com contributors
// For license information, please see license.txt
// Limit Restriction
frappe.ui.form.on('Limit Restriction', {
    refresh: function (frm) {

    },
    by_user: function (frm,dt,dn) {
        if (cur_frm.doc.by_user != "") {
            frappe.model.set_value(dt, dn, "by_role", "")
        }
    },
    by_role: function (frm, dt, dn) {
        if (cur_frm.doc.by_role != "") {
            frappe.model.set_value(dt, dn, "by_user", "")
        }
    }

});
