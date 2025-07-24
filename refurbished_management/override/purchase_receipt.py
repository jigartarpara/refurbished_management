import frappe

def on_submit(doc, method):
    message = "IMEI numbers updated successfully in Serial No records."
    for row in doc.items:
        if row.imei_no:
            for imeis in row.imei_no.split('\n'):
                try:
                    serial_no, imei_no_1, imei_no_2 = imeis.split(',')
                    serial_no_doc = frappe.get_doc("Serial No", serial_no)
                    serial_no_doc.imei_no_1 = imei_no_1.strip()
                    serial_no_doc.imei_no_2 = imei_no_2.strip()
                    serial_no_doc.save()
                    message += "\n Success Serial No: {}, IMEI No 1: {}, IMEI No 2: {}".format(
                        serial_no_doc.name,
                        serial_no_doc.imei_no_1,
                        serial_no_doc.imei_no_2
                    )
                except:
                    message += "\n <b>Failed</b> {}".format(imeis)
    frappe.msgprint(message)

