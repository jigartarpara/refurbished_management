# Copyright (c) 2025, jigartarpara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class RefurbOrder(Document):
    def onload(self):
        self.set_onload("stock_transfer", self.get_stock_transfer_data())
    
    def get_stock_transfer_data(self):
        device_transfer_entry = frappe.db.get_all("Stock Entry", {"docstatus":1,"stock_entry_type":"Transfer Device For Refurbishment", "refurb_order":self.name}, "name")
        device_return_entry = frappe.db.get_all("Stock Entry", {"docstatus":1,"stock_entry_type":"Return Device From Refurbishment", "refurb_order":self.name}, "name")
        transfer = len(device_transfer_entry) - len(device_return_entry)
        result = {}
        result["device_transfer_entry"] = True if transfer > 0 else False
        result["net_transfer_stock"] = self.get_net_transfer()
        
        return result
    
    def get_net_transfer(self):
        pass
    
    def validate(self):
        if not self.cost:
            self.get_cost()
        if not self.task_created:
            self.create_tasks()
    
    def get_cost(self):
        if self.has_serial_no:
            cost = frappe.db.sql("""
                SELECT bundle.avg_rate 
                FROM 
                    `tabSerial and Batch Bundle` as bundle,
                    `tabSerial and Batch Entry` as entry
                WHERE 
                    bundle.name = entry.parent
                    AND bundle.type_of_transaction = "Inward"
                    AND bundle.item_code = %s
                    and entry.serial_no = %s
            """, (self.item,self.serial_no), as_dict=True)
            if cost:
                self.cost = cost[0].avg_rate
            else:
                self.cost = 0.0

    def create_tasks(self):
        if self.ro_task_template:
            task_template = frappe.get_doc("RO Task Template", self.ro_task_template)
            for task in task_template.ro_task_item:
                new_task = frappe.new_doc("Task")
                new_task.subject = task.task_title
                new_task.description = task.description
                new_task.status = "Open"
                new_task.refurb_order = self.name
                new_task.insert()
            
            self.task_created = True

@frappe.whitelist()
def make_return_device(source_name,target_doc=None):
    def set_missing_values(source, target):
        rm_warehouse = frappe.db.get_single_value("Refurb Settings", "rm_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        target.stock_entry_type = "Return Device From Refurbishment"
        target.device_transfer_entry = True
        target.from_warehouse = wip_warehouse 
        target.to_warehouse = rm_warehouse
        target.append("items",{
            "s_warehouse": target.from_warehouse,
            "t_warehouse": target.to_warehouse,
            "item_code": refurb_order.item,
            "qty": 1,
            "uom": frappe.db.get_value('Item', refurb_order.item, 'stock_uom'), 
            "stock_uom": frappe.db.get_value('Item', refurb_order.item, 'stock_uom'),
            "conversion_factor": 1,
            "serial_no_batch": 1,
            "serial_no": refurb_order.serial_no
        })
        target.run_method("set_missing_values")
        

    doclist = get_mapped_doc("Refurb Order", source_name,
    {
        "Refurb Order": {
            "doctype": "Stock Entry",
            "field_map": {
                "name":"refurb_order",
            }
        },

    }, target_doc,set_missing_values)

    return doclist
@frappe.whitelist()
def make_transfer_device(source_name,target_doc=None):
    def set_missing_values(source, target):
        rm_warehouse = frappe.db.get_single_value("Refurb Settings", "rm_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        target.stock_entry_type = "Transfer Device For Refurbishment"
        target.device_transfer_entry = True
        target.from_warehouse = rm_warehouse
        target.to_warehouse = wip_warehouse
        target.append("items",{
            "s_warehouse": rm_warehouse,
            "t_warehouse": wip_warehouse,
            "item_code": refurb_order.item,
            "qty": 1,
            "uom": frappe.db.get_value('Item', refurb_order.item, 'stock_uom'), 
            "stock_uom": frappe.db.get_value('Item', refurb_order.item, 'stock_uom'),
            "conversion_factor": 1,
            "serial_no_batch": 1,
            "serial_no": refurb_order.serial_no
        })
        target.run_method("set_missing_values")
        

    doclist = get_mapped_doc("Refurb Order", source_name,
    {
        "Refurb Order": {
            "doctype": "Stock Entry",
            "field_map": {
                "name":"refurb_order",
            }
        },

    }, target_doc,set_missing_values)

    return doclist