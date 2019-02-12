// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Allocation Problems"] = {
	"filters": [
		{
			"fieldname":"sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		},
	{
	    "fieldname": "display_nm_records",
            "label": __("Display Non Matching Records?"),
            "fieldtype": "Check",
            "default": "0"
	},

	]
}

