import frappe

def on_submit(doc, method):
    if doc.stock_entry_type == "Manufacture" and doc.refurb_order:
        task = frappe.db.get_value("Task", {"refurb_order": doc.refurb_order, "status": ("!=", "Completed")}, "name")
        if task:
            frappe.throw("This Refurb Order has open task please complete it first. "+task)