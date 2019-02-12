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
        

        for (item_code) in sorted(iwb_map):
                qty_dict = iwb_map[item_code]
                data.append([
                        item_code, qty_dict.serial_number, qty_dict.brn, qty_dict.dro, qty_dict.dra, qty_dict.warehouse, qty_dict.sales_order, qty_dict.customer                        
                    ])

	for rows in data: 
			summ_data.append([rows[0], rows[1],rows[2],
			 	rows[3], rows[4], rows[5], rows[6], rows[7]
					
				])
						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [
		_("Item Code")+":Link/Item:100",
		_("Serial Number")+":Link/Serial No:100",
		_("Booking Reference Number")+"::100",
		_("Delivery Required On")+":Date:100",
		_("Delivery Required At")+"::100",
		_("Warehouse")+"::100",
		_("Sales Order")+":Link/Sales Order:100",
		_("Customer")+"::100",
         ]

        return columns

def get_conditions(filters):
        conditions = ""

	if filters.get("disp_today") == 1 and filters.get("disp_tom") == 1:
		frappe.throw(_("Both the check fields cannot be checked. Click any one"))

        if filters.get("disp_today") is None and filters.get("disp_tom") is None:
		frappe.throw(_("At least one check field should be selected"))

	if filters.get("disp_today") == 1:

		conditions += "and sn.delivery_required_on = CURDATE()"
        if filters.get("disp_tom") == 1:
		conditions += "and sn.delivery_required_on = CURDATE() + 1"

	
        return conditions

def get_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select sn.item_code as item_code, sn.name as serial_number, sn.booking_reference_number as brn,
sn.delivery_required_on as dro, sn.delivery_required_at dra, sn.warehouse as warehouse, so.name as sales_order, so.customer_name as customer
from `tabSerial No` sn, `tabSales Order` so where so.booking_reference_number = sn.booking_reference_number %s""" % conditions, as_dict=1)


def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
 #       to_date = getdate(filters["to_date"])
	
        sle = get_serial_numbers(filters)
#	kle = get_items_wo_serial_numbers(filters)

        for d in sle:
                key = (d.item_code)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                                        })

                qty_dict = iwb_map[(d.item_code)]
		
		qty_dict.serial_number = d.serial_number
                qty_dict.brn = d.brn
                qty_dict.dro = d.dro
                qty_dict.dra = d.dra	
		qty_dict.customer = d.customer
		qty_dict.warehouse = d.warehouse
		qty_dict.sales_order = d.sales_order
	
     
        return iwb_map


