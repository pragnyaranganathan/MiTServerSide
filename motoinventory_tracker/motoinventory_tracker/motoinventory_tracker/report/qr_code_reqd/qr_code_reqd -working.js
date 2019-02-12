// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QR Code Reqd"] = {
	"filters": [
		{
			"fieldname":"created_from",
			"label": __("Created Date From"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"created_to",
			"label": __("Created Date To"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"number_labels",
			"label": __("Number of Labels"),
			"fieldtype": "Data",
			"default": 1,
			"reqd": 1
		}
		
	]

}
