// Copyright (c) 2025, jigartarpara and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refurb Order", {
	refresh(frm) {
        if(!cur_frm.doc.__onload.device_transfer_entry){
            frm.add_custom_button(
                __("Transfer Device For Refurbshing"),
                function () {
                    frappe.model.open_mapped_doc({
                        method: "refurbished_management.refurbished_management.doctype.refurb_order.refurb_order.make_transfer_device",
                        frm: cur_frm,
                    });
                },
                "Device Transfer"
            );
        }
        if(cur_frm.doc.__onload.device_transfer_entry){
            frm.add_custom_button(
                __("Return Device From Refurbshing"),
                function () {
                    frappe.model.open_mapped_doc({
                        method: "refurbished_management.refurbished_management.doctype.refurb_order.refurb_order.make_return_device",
                        frm: cur_frm,
                    });
                },
                "Device Transfer"
            );
        }
        frm.add_custom_button(
            __("Transfer Part For Refurbshing"),
            function () {
                frappe.model.open_mapped_doc({
                    method: "refurbished_management.refurbished_management.doctype.refurb_order.refurb_order.make_part_trasnfer",
                    frm: cur_frm,
                });
                
            }, 
            "Part Transfer"
        );
        frm.add_custom_button(
            __("Return Part From Refurbshing"),
            function () {
                frappe.model.open_mapped_doc({
                    method: "refurbished_management.refurbished_management.doctype.refurb_order.refurb_order.make_part_return",
                    frm: cur_frm,
                });
            },
            "Part Transfer"
        );
        frm.add_custom_button(
            __("FG Entry For Refurbshing"),
            function () {
                frappe.model.open_mapped_doc({
                    method: "refurbished_management.refurbished_management.doctype.refurb_order.refurb_order.make_fg_entry",
                    frm: cur_frm,
                });
            },
            "Final Entry"
        );
        net_qty = cur_frm.doc.__onload.net_transfer_stock;
        cur_frm.fields_dict.issue_materials.$wrapper.html(net_qty)
	},
});
