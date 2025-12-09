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
# ---------------------------------------------------------
# SIGN REDIRECT OVERRIDE (IMPORTANT)
# ---------------------------------------------------------

class SignRedirectOverride(Sign):

    @http.route(
        ['/sign/document/<int:request_id>/<string:access_token>/complete'],
        type='http', auth='public', website=True, csrf=False
    )
    def sign_validate(self, request_id, access_token, **post):

        # Run Odoo’s original signature completion logic
        res = super(SignRedirectOverride, self).sign_validate(
            request_id, access_token, **post
        )

        # If Odoo wants to redirect to /my/signature/<id>, override it
        if isinstance(res, http.RedirectResponse) and "/my/signature/" in res.location:
            return request.redirect("/my/employee/sign")

        return res