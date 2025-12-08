# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class EmployeePortalSignDocs(CustomerPortal):

    @http.route('/my/employee/sign', type='http', auth='user', website=True)
    def portal_employee_sign_docs(self, **kwargs):
        user = request.env.user

        # If Sign module not installed
        if "sign.request.item" not in request.env:
            sign_items = []
        else:
            # get items assigned to current user AND still waiting to sign
            sign_items = request.env["sign.request.item"].sudo().search([
                ('partner_id', '=', user.partner_id.id),
                ('state', '=', 'sent')    # IMPORTANT: correct state
            ])

        return request.render("employee_portal_suite.portal_sign_documents_page", {
            "sign_items": sign_items
        })
