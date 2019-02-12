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
        
	disp_nm_records = filters.get("display_nm_records")
	

        for (sales_order, item_code) in sorted(iwb_map):
                qty_dict = iwb_map[sales_order, item_code]
                data.append([
                        qty_dict.brn, sales_order, qty_dict.customer, qty_dict.delivery_date, qty_dict.status, qty_dict.delivery_status, item_code, qty_dict.serial_number, qty_dict.serial_item
                        
                    ])

	for rows in data: 

		if disp_nm_records == 1:
			if rows[6] != rows[8]:
				summ_data.append([rows[0], rows[1],rows[2],
			 	rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]
					
				])
		else:
			summ_data.append([rows[0], rows[1],rows[2],
			 	rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]
					
				])
						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [
		_("Booking Reference Number")+"::100",
		_("Sales Order")+":Link/Sales Order:100",
		_("Customer")+"::100",
		_("Delivery Date")+"::150",
		_("Status")+"::100",
		_("Delivery Status")+"::100",
		_("Item Code(SO)")+":Link/Item:100",
		_("Serial Number")+"::100",
		_("Item Code (SN)")+"::100"
		
         ]

        return columns

def get_conditions(filters):
        conditions = ""

        if filters.get("sales_order"):
		conditions += " and so.name = '%s'" % frappe.db.escape(filters.get("sales_order"), percent=False)

        if filters.get("item_code"):
			conditions += " and si.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

	
        return conditions

def get_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select so.booking_reference_number as brn, so.name as sales_order, so.customer as customer, so.delivery_date as del_date, so.status as status, so.delivery_status as delivery_status, si.item_code as item_code, sn.name as serial_number, sn.item_code as serial_item from `tabSales Order` so, `tabSales Order Item` si, `tabSerial No` sn where so.name = si.parent and so.booking_reference_number = sn.booking_reference_number and so.delivery_status = "Not Delivered" and so.status != "Cancelled" and so.booking_reference_number != "" %s order by so.name, si.item_code, sn.name"""  % conditions, as_dict=1)

def get_items_wo_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select so.booking_reference_number as brn, so.name as sales_order, so.customer as customer, so.delivery_date as del_date, so.status as status, so.delivery_status as delivery_status, si.item_code as item_code, "" as serial_number, "" as serial_item from `tabSales Order` so, `tabSales Order Item` si where so.name = si.parent and so.delivery_status = "Not Delivered"  and so.status != "Cancelled" and so.booking_reference_number != "" %s and not exists (select 1 from `tabSerial No` sn where sn.booking_reference_number = so.booking_reference_number) order by so.name, si.item_code"""  % conditions, as_dict=1)


def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
 #       to_date = getdate(filters["to_date"])
	
        sle = get_serial_numbers(filters)
#	kle = get_items_wo_serial_numbers(filters)

        for d in sle:
                key = (d.sales_order, d.item_code)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                                        })

                qty_dict = iwb_map[(d.sales_order, d.item_code)]

                qty_dict.brn = d.brn
		qty_dict.customer = d.customer
		qty_dict.delivery_date = d.del_date
		qty_dict.status = d.status
		qty_dict.delivery_status = d.delivery_status
		qty_dict.serial_number = d.serial_number
		qty_dict.serial_item = d.serial_item	

#	if kle:

 #       	for d in kle:
#	                key = (d.sales_order, d.item_code)
 #       	        if key not in iwb_map:
  #      	                iwb_map[key] = frappe._dict({
#                                                        })

   #     	        qty_dict = iwb_map[(d.sales_order, d.item_code)]

    #    	        qty_dict.brn = d.brn
	#		qty_dict.customer = d.customer
	#		qty_dict.delivery_date = d.del_date
	#		qty_dict.status = d.status
	#		qty_dict.delivery_status = d.delivery_status
	#		qty_dict.serial_number = d.serial_number
	#		qty_dict.serial_item = d.serial_item		
	
     
        return iwb_map


