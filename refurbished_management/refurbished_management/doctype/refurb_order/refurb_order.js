// Copyright (c) 2025, jigartarpara and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refurb Order", {
	refresh(frm) {
        if(!cur_frm.doc.__onload.stock_transfer.device_transfer_entry){
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
        if(cur_frm.doc.__onload.stock_transfer.device_transfer_entry){
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
                
            }, 
            "Part Transfer"
        );
        frm.add_custom_button(
            __("Return Part From Refurbshing"),
            function () {
                
            },
            "Part Transfer"
        );
        frm.add_custom_button(
            __("FG Entry For Refurbshing"),
            function () {
                
            },
            "Final Entry"
        );
	},
});
