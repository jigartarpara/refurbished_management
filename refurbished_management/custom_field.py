from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import frappe

def setup_custom_fields():
	custom_fields = {
		"Stock Entry": [
			dict(fieldname='refurb_order',
				label='Refurb Order',
				fieldtype='Link',
				options='Refurb Order',
				insert_after='work_order',
				set_only_once=True
			),
		],
		"Task": [
			dict(fieldname='refurb_order',
				label='Refurb Order',
				fieldtype='Link',
				options='Refurb Order',
				insert_after='subject',
				set_only_once=True
			)
		],
		"Item": [
			dict(fieldname='task_template',
				label='RO Task Template',
				fieldtype='Link',
				options='RO Task Template',
				insert_after='item_group',
			),
			dict(fieldname='refurb_fg_item',
				label='Refurb FG Item',
				fieldtype='Link',
				options='Item',
				insert_after='task_template',
			),
		],
		"Purchase Receipt Item": [
			dict(fieldname='imei_no',
				label='IMEI No',
				fieldtype='Text',
				insert_after='batch_no',
				description='Enter the IMEI number of the item. Serial No, IMEINO1, IMEINO2'
			)
        ],
		"Serial No": [
			dict(fieldname='imei_no_1',
				label='IMEI No 1',
				fieldtype='Data',
				insert_after='brand',
			),
			dict(fieldname='imei_no_2',
				label='IMEI No 2',
				fieldtype='Data',
				insert_after='imei_no_1',
			)
        ]
	}
	try:
		create_custom_fields(custom_fields)
		frappe.db.commit()
	except:
		print("Exception while createing customfield")