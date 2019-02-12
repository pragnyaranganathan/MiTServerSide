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
        prev_item = ""
	work_item = ""
	qty = 0
	loop_count = 0
        iwb_map = get_item_map(filters)

        data = []
        


        for (item_code, unallot_stock) in sorted(iwb_map):
                qty_dict = iwb_map[item_code, unallot_stock]

                data.append([
                        item_code, unallot_stock
                        
                    ])

	for rows in data:
		if loop_count == 0:
			work_item = rows[0]
			prev_item = rows[0]
			qty = rows[1]
		else:
			work_item = rows[0]
			if prev_item == work_item:
				qty = qty + rows[1]

			else:
				summ_data.append([prev_item, qty])
				prev_item = work_item
				qty = 0
#				summ_data.append([work_item, qty])
		
		loop_count = loop_count + 1

	summ_data.append([work_item, qty])


						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [
		_("Item Code")+":Link/Item:100",
		_("Unallocated Stock")+"::100",
		
         ]

        return columns

def get_conditions(filters):
        conditions = ""

        if filters.get("item_code"):
			conditions += " and si.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

	
        return conditions

def get_serial_numbers(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select sn.item_code as item_code, count(*) as unallot_stock
from `tabSerial No` sn where sn.booking_reference_number is Null and sn.vehicle_status != "Delivered" %s
GROUP BY sn.item_code"""  % conditions, as_dict=1)

def get_items_allocated(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select sn.item_code as item_code, 0 as unallot_stock
from `tabSerial No` sn where not exists (Select 1 from `tabSerial No` sn2 where sn2.booking_reference_number is not Null and sn.vehicle_status = "Delivered") %s
GROUP BY sn.item_code"""  % conditions, as_dict=1)


def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
 #       to_date = getdate(filters["to_date"])
	
        sle = get_serial_numbers(filters)

	kle = get_items_allocated(filters)

#	kle = get_items_wo_serial_numbers(filters)

        for d in sle:
                key = (d.item_code, d.unallot_stock)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                                        })

                qty_dict = iwb_map[(d.item_code, d.unallot_stock)]


	if kle:
 		for d in kle:
	                key = (d.item_code, d.unallot_stock)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
				
                                                        })

        	        qty_dict = iwb_map[(d.item_code, d.unallot_stock)]

     
        return iwb_map


