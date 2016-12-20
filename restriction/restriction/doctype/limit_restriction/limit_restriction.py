# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz.zone@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import  flt
class LimitRestriction(Document):
	pass
	def validate (self):
		passed=False
		field = frappe.db.sql(""" select fieldtype from tabDocField where parent='{}' and fieldname='{}' """
			.format(self.form,self.currency_field),as_list=1)
		for row in field:
			if row[0]=='Currency':
				passed=True
		if not passed:
			frappe.throw("Field is not right!!")
		#if self.period == 'By Transaction':
		rule = frappe.db.sql("""select title from `tabLimit Restriction` where disable=0 and form='{}' and currency_field='{}' and period='{}' and user='{}' """
			.format(self.form,self.currency_field,self.period,self.user),as_list=1)
		for row in rule:
			frappe.throw("Duplicate rules found {} ".format(row[0]))
		
def check_restriction(doc,method):
	rule = frappe.db.sql("""select `currency_field`,`limit_value`,period,days,date_field from `tabLimit Restriction` where form='{}' and disable=0 and user='{}' 
		""".format(doc.doctype,frappe.session.user),as_list=1)
	for row in rule:
		if row[2]=="By Transaction" :
			if flt(doc.get(row[0]))>flt(row[1]):
				frappe.throw("You Cant Create This document because overlimit maximum alowed transaction is {} ".format(row[1]))
		else:
			data = frappe.db.sql("""select sum({}) from `tab{}` where docstatus=1 and ({} between CURDATE() and DATE_SUB(CURDATE(),INTERVAL {} DAY)) """
				.format(row[0],doc.doctype,row[4],row[3]),as_list=1)
			for trx in data:
				if flt(trx[0])+flt(doc.get(row[0]))>flt(row[1]):
					frappe.throw("You Cant Create This document because overlimit maximum alowed transaction is {} for last {} day".format(row[1],row[3]))
	
