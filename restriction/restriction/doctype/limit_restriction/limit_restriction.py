# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz.zone@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,fmt_money


class LimitRestriction(Document):
    def validate(self):
        passed = False
        field = frappe.db.sql("""select fieldtype from tabDocField where parent='{}' and fieldname='{}' """
                                  .format(self.form, self.currency_field), as_list=1)
        for row in field:
            if row[0] == 'Currency':
                passed = True
        if not passed:
            frappe.throw("Inappropriate field used as currency field.")

        limit = frappe.db.sql("""select name from `tabLimit Restriction` where form='{}' and user='{}' """
                                  .format(self.form, self.user), as_list=1)
        err = "Sorry... Transaction limit already exist for {} on {}".format(self.user, self.form)
        if self.get('__islocal') and limit:
            frappe.throw(err)
        else:
            if limit and limit[0][0] != self.name:
                frappe.throw(err)


def check_restriction(doc, method):
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
                frappe.throw("Sorry, You can not create this document because {} is above your maximum transaction limit of {} pay transaction".
                             format(fmt_money(flt(doc.get(row[0]))), fmt_money(row[1]) ))
        else:
            qry = """select sum({}) from `tab{}` where docstatus=1
                                    and (DATE(`{}`) between DATE_SUB(CURDATE(),INTERVAL {} DAY) and CURDATE()) and modified_by='{}'""".format(
                row[0], row[5], row[4], row[3], row[6])
            data = frappe.db.sql(qry, as_list=0)
            #frappe.errprint(qry)

            for transaction in data:
                if flt(transaction[0]) + flt(doc.get(row[0])) > flt(row[1]):
                    if row[3] == 1 : day = "a day"
                    else: day = str(row[3])+ " days"
                    frappe.throw("Sorry, You can not create this document because {} is above your maximum transaction limit of {} in {}"
                                 .format(fmt_money(flt(transaction[0]) + flt(doc.get(row[0]))), fmt_money(row[1]),day) )
