# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz.zone@gmail.com, masonarmani38@gmail.com and Contributors
# See license.txt
from __future__ import unicode_literals
from frappe.utils.data import flt
from frappe import  get_doc, get_conf, set_user, get_user
import frappe
import unittest


# test_records = frappe.get_test_records('Restriction')

class TestLimitRestriction(unittest.TestCase):
    def test_limitation(self):
        set_user("masonarmani38@gmail.com")
        doc = get_doc("Expense Claim", "GCL-EXP-02725") # Assuming this is a temporary file
        # check if the user has a limitation
        rule = frappe.db.sql("""select `currency_field`,`limit_value`,`period` ,`days`, `date_field`, `form` ,`user` from `tabLimit Restriction`
                                  where form='{}' and disable=0 and user='{}'""".format(doc.doctype, frappe.session.user),
                             as_list=1)
        for row in rule:
            """
                row[0] holds the currency field used in the doctype / form
                row[1] holds the limit value
                row[2] holds the restriction type
                row[3] holds the number of days restriction applies if the restriction type is per day
                row[4] holds the date field used in the doctype / form
                row[5] holds the doctype / form
                row[6] holds the user the limitation is on doctype / form
            """
            if row[2] == "By Transaction":
                if flt(doc.get(row[0])) > flt(row[1]):
                    frappe.throw("Sorry, You can not create this document because over limit maximum "
                                 "allowed transaction is {} ".format(row[1]))
            else:
                qry = """select sum({}) from `tab{}` where docstatus=1
                                        and ({} between DATE_SUB(CURDATE(),INTERVAL {} DAY) and CURDATE()) and owner='{}' """.format(row[0], row[5], row[4], row[3], row[6])
                data = frappe.db.sql(qry, as_list=0)
                for transaction in data:
                    if flt(transaction[0]) + flt(doc.get(row[0])) > flt(row[1]):
                        frappe.throw("Sorry, You can not create this document because over limit maximum allowed "
                                     "transaction is {} for last {} day".format(row[1], row[3]))
