# Copyright (c) 2025, jigartarpara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RefurbOrder(Document):
	def validate(self):
		if not self.cost:
			self.get_cost()
		if not self.task_created:
			self.create_tasks()
	
	def get_cost(self):
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