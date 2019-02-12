
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime


@frappe.whitelist()
def test_method(warehouse):

	records = frappe.db.sql("""select item_code, stock_uom from `tabStock Ledger Entry` sle where sle.warehouse = %(string2)s""", {'string2':warehouse})
	if records:
		return records
