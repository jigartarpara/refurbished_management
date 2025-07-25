# Copyright (c) 2025, jigartarpara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class RefurbOrder(Document):
    def onload(self):
        self.get_stock_transfer_data()
    
    def get_stock_transfer_data(self):
        device_transfer_entry = frappe.db.get_all("Stock Entry", {"docstatus":1,"stock_entry_type":"Transfer Device For Refurbishment", "refurb_order":self.name}, "name")
        device_return_entry = frappe.db.get_all("Stock Entry", {"docstatus":1,"stock_entry_type":"Return Device From Refurbishment", "refurb_order":self.name}, "name")
        manufacturing = frappe.db.get_value("Stock Entry",{"docstatus":1,"stock_entry_type":"Manufacture", "refurb_order":self.name}, "name" )
        transfer = len(device_transfer_entry) - len(device_return_entry)
        self.set_onload("device_transfer_entry", True if transfer > 0 else False)
        self.set_onload("net_transfer_stock", frappe.render_template('refurbished_management/templates/issue_materials.html', {
            'final_data': self.get_net_transfer(),
            'manufacturing': manufacturing,
            'device_transfer': True if transfer > 0 else False
        }))
        
        self.set_onload("manufacturing",True if manufacturing else False)
        draft_manufacturing = frappe.db.get_value("Stock Entry",{"docstatus":0,"stock_entry_type":"Manufacture", "refurb_order":self.name}, "name" )
        self.set_onload("draft_manufacturing",draft_manufacturing if draft_manufacturing else False)
        

    
    def get_net_transfer(self):
        transfer_entry_type = ["Transfer For Refubishment", "Transfer Device For Refurbishment"]
        return_entry_type = ["Return From Refurbishment", "Return Device From Refurbishment"]
        transfer_entry = frappe.db.sql("""
            SELECT 
                item.item_code, item.qty,item.serial_no, se.stock_entry_type
            from
                `tabStock Entry Detail` as item,
                `tabStock Entry` as se
            WHERE
                item.parent = se.name
                AND se.docstatus = 1
                AND se.refurb_order = %s
                                
        """, (self.name), as_dict=True)
        net_qty = {}
        for row in transfer_entry:
            if row.stock_entry_type in transfer_entry_type:
                temp_data = net_qty.get(row.item_code, {})
                temp_data["qty"] = temp_data.get("qty", 0) + row.qty
                serial_no = temp_data.get("serial_no", [])
                if row.serial_no and row.serial_no not in serial_no:
                    serial_no.append(row.serial_no)
                temp_data["serial_no"] = serial_no
                net_qty[row.item_code] = temp_data
            elif row.stock_entry_type in return_entry_type:
                temp_data = net_qty.get(row.item_code, {})
                temp_data["qty"] = temp_data.get("qty", 0) - row.qty
                serial_no = temp_data.get("serial_no", [])
                if row.serial_no and row.serial_no in serial_no:
                    serial_no.remove(row.serial_no)
                temp_data["serial_no"] = serial_no
                net_qty[row.item_code] = temp_data
        final_data = []
        for item_code, data in net_qty.items():
            final_data.append({
                "item_code": item_code,
                "serial_no": ", ".join(data.get("serial_no", [])),
                "qty": data.get("qty", 0),
            })
        return final_data
    
    def validate(self):
        manufacturing = frappe.db.get_value("Stock Entry",{"docstatus":1,"stock_entry_type":"Manufacture", "refurb_order":self.name}, "name" )
        if manufacturing:
            frappe.throw("Changes Not Allowed After Manufacturing Entry.")
        if not self.cost:
            self.get_cost()
        if not self.task_created:
            self.create_tasks()
        if not self.fg_serial_no:
            self.fg_serial_no = self.serial_no + " - FG"
        
    
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
def make_fg_entry(source_name,target_doc=None):
    def set_missing_values(source, target):
        fg_warehouse = frappe.db.get_single_value("Refurb Settings", "fg_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        scrap_warehouse = frappe.db.get_single_value("Refurb Settings", "scrap_warehouse")
        
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        net_transfer = refurb_order.get_net_transfer()
        target.stock_entry_type = "Manufacture"
        target.from_warehouse = wip_warehouse 
        target.to_warehouse = fg_warehouse
        for row in net_transfer:
            target.append("items",{
                "s_warehouse": target.from_warehouse,
                "item_code": row.get("item_code"),
                "qty": row.get("qty"),
                "uom": frappe.db.get_value('Item', row.get("item_code"), 'stock_uom'), 
                "stock_uom": frappe.db.get_value('Item', row.get("item_code"), 'stock_uom'),
                "conversion_factor": 1,
                "serial_no_batch": 1,
                "serial_no": row.get("serial_no","")
            })
        
        target.append("items",{
            "t_warehouse": target.to_warehouse,
            "item_code": refurb_order.fg_item,
            "qty": 1,
            "uom": frappe.db.get_value('Item', refurb_order.fg_item, 'stock_uom'), 
            "stock_uom": frappe.db.get_value('Item', refurb_order.fg_item, 'stock_uom'),
            "conversion_factor": 1,
            "serial_no_batch": 1,
            "is_finished_item": 1,
            "serial_no": refurb_order.fg_serial_no
        })
        for row in refurb_order.scrap_item:
            target.append("items",{
                "t_warehouse": scrap_warehouse,
                "item_code": row.get("item_code"),
                "qty": row.get("qty"),
                "basic_rate": row.get("value"),
                "uom": frappe.db.get_value('Item', row.get("item_code"), 'stock_uom'), 
                "stock_uom": frappe.db.get_value('Item', row.get("item_code"), 'stock_uom'),
                "conversion_factor": 1,
                "serial_no_batch": 1,
                "is_scrap_item": 1,
                "serial_no": row.get("serial_no","")
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
def make_part_return(source_name,target_doc=None):
    def set_missing_values(source, target):
        rm_warehouse = frappe.db.get_single_value("Refurb Settings", "rm_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        target.stock_entry_type = "Return From Refurbishment"
        target.from_warehouse = wip_warehouse 
        target.to_warehouse = rm_warehouse
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
def make_part_trasnfer(source_name,target_doc=None):
    def set_missing_values(source, target):
        rm_warehouse = frappe.db.get_single_value("Refurb Settings", "rm_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        target.stock_entry_type = "Transfer For Refubishment"
        target.from_warehouse = rm_warehouse  
        target.to_warehouse = wip_warehouse
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
def make_return_device(source_name,target_doc=None):
    def set_missing_values(source, target):
        rm_warehouse = frappe.db.get_single_value("Refurb Settings", "rm_warehouse")
        wip_warehouse = frappe.db.get_single_value("Refurb Settings", "wip_warehouse")
        
        refurb_order = frappe.get_doc("Refurb Order", source_name)
        target.stock_entry_type = "Return Device From Refurbishment"
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