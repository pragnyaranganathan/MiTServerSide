// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Dispatch Statement"] = {
	"filters": [
		
	{
	    "fieldname": "disp_today",
            "label": __("Show Dispatch schedule for today"),
            "fieldtype": "Check"
	},
	{
	    "fieldname": "disp_tom",
            "label": __("Show Dispatch schedule for tomorrow"),
            "fieldtype": "Check",
            "default": "1"
	}

	]
}

