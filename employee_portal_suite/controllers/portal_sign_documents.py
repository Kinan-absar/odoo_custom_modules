# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class EmployeePortalSignDocs(CustomerPortal):

    @http.route('/my/employee/sign', type='http', auth='user', website=True)
    def portal_employee_sign_docs(self, filter="pending", **kwargs):
        user = request.env.user
        SignItem = request.env["sign.request.item"].sudo()

        # Filter mapping
        domain_map = {
            "pending": [('partner_id', '=', user.partner_id.id), ('state', '=', 'sent')],
            "signed":  [('partner_id', '=', user.partner_id.id), ('state', '=', 'completed')],
            "rejected": [('partner_id', '=', user.partner_id.id), ('state', '=', 'canceled')],
        }

        domain = domain_map.get(filter, domain_map["pending"])
        sign_items = SignItem.search(domain)

        return request.render("employee_portal_suite.portal_sign_documents_page", {
            "sign_items": sign_items,
            "current_filter": filter,
        })
