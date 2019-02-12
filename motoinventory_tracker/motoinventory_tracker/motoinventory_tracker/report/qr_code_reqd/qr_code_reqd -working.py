# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime,comma_and
from collections import defaultdict
import frappe
import json
import time
import math
import ast

def execute(filters=None):
	global summ_data
        if not filters: filters = {}

        columns = get_columns()
       
        iwb_map = get_item_map(filters)

        data = []
        
	summ_data = []
	diff_data = 0	

        for (item_code, serial_number) in sorted(iwb_map):
                qty_dict = iwb_map[item_code, serial_number]
                data.append([
                        serial_number, item_code, qty_dict.warehouse, qty_dict.delivery_required_at, qty_dict.delivery_required_on, qty_dict.vehicle_status, qty_dict.creation
                        
                    ])

	for rows in data: 

		created_date = getdate(rows[6])
		created_from = getdate(filters.get("created_from"))
		created_to = getdate(filters.get("created_to"))
		number_labels = filters.get("number_labels")
		if ((created_date >= created_from) and (created_date <= created_to)):
			string_qr = "http://www.barcodes4.me/barcode/qr/myfilename.png?value=" + rows[0]

		
			summ_data.append([rows[0], rows[1],rows[2],
		 	rows[3], rows[4], rows[5], rows[6], number_labels
				
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
		_("Number of labels")+"::10"
		
         ]

        return columns

def get_conditions(filters):
        conditions = ""
        if filters.get("created_from"):
		created_date = getdate(filters.get("created_from"))

		conditions += " and sn.creation = '%s'" % frappe.db.escape(filters["created_from"])

	
        return conditions

def get_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select name as serial_number, item_code as item_code, warehouse, delivery_required_at, delivery_required_on, vehicle_status, creation
                from `tabSerial No` sn
                where sn.vehicle_status = "Invoiced but not Received" order by sn.item_code, sn.name""", as_dict=1)


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



