#!/usr/bin/python
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
#import flask
import frappe
import json
import time
import math
import ast
import os.path
import sys
print sys.path

from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime,comma_and
from collections import defaultdict
from werkzeug.wrappers import Response


reload(sys)
sys.setdefaultencoding('utf-8')



def execute(filters=None):
	global summ_data
	global data
	global number_labels
	global warehouse
	summ_data = []
        if not filters: filters = {}

        columns = get_columns()
       
        iwb_map = get_item_map(filters)

        data = []
        
	diff_data = 0
	print_qr = 0

        for (item_code, serial_number) in sorted(iwb_map):
                qty_dict = iwb_map[item_code, serial_number]
                data.append([
                        serial_number, item_code, qty_dict.warehouse, qty_dict.delivery_required_at, qty_dict.delivery_required_on, qty_dict.vehicle_status, qty_dict.creation, print_qr
                        
                    ])

	number_labels = filters.get("number_labels")
	for rows in data: 

		created_date = getdate(rows[6])
		created_from = getdate(filters.get("created_from"))
		created_to = getdate(filters.get("created_to"))
	
		if ((created_date >= created_from) and (created_date <= created_to)):
					
			summ_data.append([rows[0], rows[1],rows[2],
		 	rows[3], rows[4], rows[5], rows[6], number_labels, rows[7]
				
			]) 
						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [
		_("Serial Number")+"::100",
		_("Item Code")+"::100",
		_("Warehouse")+"::100",
		_("Delivery Required At")+"::150",
		_("Delivery Required On")+"::100",
		_("Vehicle Status")+"::100",
		_("Creation Date")+":Date:100",
		_("Number of labels")+"::10",
		_("Print QR Code")+":Check:10"
		
         ]

        return columns

def get_conditions(filters):
        conditions = ""

        if filters.get("vehicle_status"):
		veh_status = filters.get("vehicle_status")
		if veh_status != "All":
			conditions += " where sn.vehicle_status = '%s'" % frappe.db.escape(filters.get("vehicle_status"), percent=False)

#        if filters.get("created_from"):
#		created_date = getdate(filters.get("created_from"))

#		conditions += " and sn.creation = '%s'" % frappe.db.escape(filters["created_from"])

        if filters.get("warehouse"):
		warehouse = filters.get("warehouse")
		if veh_status != "All":
			conditions += " and sn.warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)
		else:
			conditions += " where sn.warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)


	
        return conditions

def get_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select name as serial_number, item_code as item_code, warehouse, delivery_required_at, delivery_required_on, vehicle_status, creation
                from `tabSerial No` sn %s order by sn.item_code, sn.name"""  % conditions, as_dict=1)


def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
 #       to_date = getdate(filters["to_date"])
	
        sle = get_serial_numbers(filters)

        for d in sle:
                key = (d.item_code, d.serial_number)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                "si_qty": 0.0,
                        })

                qty_dict = iwb_map[(d.item_code, d.serial_number)]

                
                qty_dict.warehouse = d.warehouse
		qty_dict.delivery_required_at = d.delivery_required_at
		qty_dict.delivery_required_on = d.delivery_required_on
		qty_dict.vehicle_status = d.vehicle_status
		qty_dict.creation = d.creation
		
     
        return iwb_map

@frappe.whitelist()
def choose_records(args):

#	creation_Date = getdate(datetime.now().strftime('%Y-%m-%d'))

	ret = ""
	innerJson_Transfer = " "

	outerJson_Transfer = {
				"doctype": "QR Code",
				"number_of_labels": number_labels,
				"items": [
	]}
	
	print "######-summ_data::", summ_data
	for rows in summ_data:	
		
		print "######-item_code::", rows[0]
		innerJson_Transfer = {
					"serial_number": rows[0],
					"item_code": rows[1],
					"warehouse": rows[2],
					"vehicle_status": rows[5],
					"creation_date": rows[6],
					"doctype": "QR Code Item",
					"parenttype": "QR Code",
					"parentfield": "items"
				  	}
		outerJson_Transfer["items"].append(innerJson_Transfer)


	doc = frappe.new_doc("QR Code")
	print "outerJson_Transfer::", outerJson_Transfer
	doc.update(outerJson_Transfer)

	doc.save()
		
	print "###-Document is saved."

	#doc.submit()
	print "###-Document is submitted."
	ret = doc.doctype
	docid = doc.name
	print "## Docid:", doc.name

	if ret:

		return docid

	
@frappe.whitelist()
def make_text(args):
	curr_date = utils.today()
	fname = "qrcode"+curr_date+".csv"
	save_path = 'site1.local/private/files'
	file_name = os.path.join(save_path, fname)
	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home"
	ferp.is_private = 1
	ferp.file_url = "/private/files/"+fname

	f= open(file_name,"w+")

	f.write("^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA")
	f.write("^PR2,2~SD15^JUS^LRN^CI0^XZ")
	f.write("^XA^MMT^PW812^LL0406^LS0")

#	txt = "^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR2,2~SD15^JUS^LRN^CI0^XZ^XA^MMT^PW812^LL0406^LS0"
	for rows in summ_data:	

##		number_labels = int(number_labels)
		nol = int(number_labels) + 1
		for x in xrange(1, nol):
			f.write("^FT250,79^A0R,28,28^FH\^FD%s^FS" % (rows[0]))
			f.write("^FT533,53^A0R,28,28^FH\^FD%s^FS" % (rows[1]))
			f.write("^FT300,301^BQN,2,8^FH\^FDMA1%s^FS" % (rows[0]))
			f.write("^PQ1,0,1,Y^XZ")
#			txt += "^FT250,79^A0R,28,28^FH\^FD%s^FS" % rows[0]
#	f.insert(txt)
	frappe.msgprint(_("Text File created - Please check File List to download the file"))
	ferp.save()
	f.close()


#	download_file()


def download_file():
	print("Inside Download")
	response = Response()
	filename = "qrcode.txt"
	frappe.response.filename = "qrcode.txt"
	response.mimetype = 'text/plain'
	response.charset = 'utf-8'
	with open("site1.local/public/files/qrcode.txt", "rb") as fileobj:
		filedata = fileobj.read()
	print("Created Filedata")
	frappe.response.filecontent = filedata
	print("Created Filecontent")
	response.type = "download"
	response.headers[b"Content-Disposition"] = ("filename=\"%s\"" % frappe.response['filename'].replace(' ', '_')).encode("utf-8")
	response.data = frappe.response['filecontent']
	print(frappe.response)
#	frappe.tools.downloadify(filename);
#	return frappe.response




