# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz.zone@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, fmt_money


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

        if self.by_user:
            limit = frappe.db.sql("""select name from `tabLimit Restriction` where form='{}' and by_user='{}' """
                                  .format(self.form, self.by_user), as_list=1)
            check = self.by_user

        elif self.by_role:
            limit = frappe.db.sql("""select name from `tabLimit Restriction` where form='{}' and by_role='{}' """
                                  .format(self.form, self.by_role), as_list=1)
            check = self.by_role

        err = "Sorry... Transaction limit already exist for {} on {}".format(check, self.form)
        if self.get('__islocal') and limit:
            frappe.throw(err)
        else:
            if limit and limit[0][0] != self.name:
                frappe.throw(err)


def check_restriction(doc, method):
    frappe.errprint(method)
    # check if the user has a limitation
    rule1 = frappe.db.sql("""select `currency_field`,`limit_value`,`period` ,`days`, `date_field`, `form`,
      `by_user`,`by_role`,`target_action` from `tabLimit Restriction`
                              where form='{}' and disable=0 and by_user='{}'""".format(doc.doctype,
                                                                                       frappe.session.user),
                         as_list=1)

    if not rule1:
        # get all the roles in the limit and then check if the user has that role
        # all roles in limit
        roles = frappe.db.sql("""select DISTINCT by_role from `tabLimit Restriction`""" , as_list=1)

        if roles:
            # filter out the None...
            _roles = [x[0] for x in roles if x[0] != None]

            # not the best way but...
            if _roles:
                str_roles = ""
                for _role in _roles:
                    str_roles += "'%s'," % _role

                str_roles = "(%s)" % str_roles.rstrip(",")

                role = frappe.db.sql("""select role from `tabHas Role` where parent='{}' and role in {} """
                                  .format(frappe.session.user, str_roles), as_list=1)

                if role:
                    rule1 = frappe.db.sql("""select `currency_field`,`limit_value`,`period` ,`days`, `date_field`, 
                                        `form`,`by_user`,`by_role`,`target_action` from `tabLimit Restriction`
                                              where form='{}' and disable=0 and by_role='{}'""".format(
                        doc.doctype,role[0][0]),as_list=1)


    for row in rule1:
        """
            row[0] holds the currency field used in the doctype / form
            row[1] holds the limit value
            row[2] holds the restriction type
            row[3] holds the number of days restriction applies if the restriction type is per day
            row[4] holds the date field used in the doctype / form
            row[5] holds the doctype / form
            row[6] holds the user the limitation is on doctype / form
            row[7] holds the role the limitation is on doctype / form
            row[8] holds the target action
        """

        status_used = "workflow_state"
        if str(row[5]) == str("Expense Claim"):
            status_used = "approval_status"

        if doc.get(status_used) == str(row[8]):
            if row[2] == "By Transaction":
                if flt(doc.get(row[0])) > flt(row[1]):
                    frappe.throw(
                        "Sorry, You can not save this document because {} is above your maximum transaction limit of {} pay transaction".
                            format(fmt_money(flt(doc.get(row[0]))), fmt_money(row[1])))
            else:
                qry = """select sum({}) from `tab{}` where docstatus=1
                                        and (DATE(`{}`) between DATE_SUB(CURDATE(),INTERVAL {} DAY) and CURDATE()) and modified_by='{}'""".format(
                    row[0], row[5], row[4], row[3], row[6])
                data = frappe.db.sql(qry, as_list=0)

                for transaction in data:
                    if flt(transaction[0]) + flt(doc.get(row[0])) > flt(row[1]):
                        if row[3] == 1:
                            day = "a day"
                        else:
                            day = str(row[3]) + " days"
                        frappe.throw(
                            "Sorry, You can not create this document because {} is above your maximum transaction limit of {} in {}"
                                .format(fmt_money(flt(transaction[0]) + flt(doc.get(row[0]))), fmt_money(row[1]), day))
