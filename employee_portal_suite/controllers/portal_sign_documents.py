# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EmployeePortalSignDocs(CustomerPortal):

    # -------------------------------
    # Helper: Your personal status
    # -------------------------------
    def _compute_personal_status(self, item):
        state = item.state

        if state in ("draft", "sent"):
            return "🟡 Pending"
        if state == "completed":
            return "🟢 Signed"
        if state == "canceled":
            return "🔴 Rejected"

        return "⚪ Unknown"

    # -------------------------------
    # Helper: Workflow timeline status
    # -------------------------------
    def _compute_workflow_status(self, sign_request):
        items = sign_request.request_item_ids

        # Fully Signed
        if all(it.state == "completed" for it in items):
            return "🟢 Fully Signed"

        # Rejected by someone
        canceled = next((it for it in items if it.state == "canceled"), None)
        if canceled:
            name = canceled.partner_id.name or "Unknown"
            return f"🔴 Rejected by {name}"

        # Next signer
        next_item = next((it for it in items if it.state != "completed"), None)
        if next_item:
            current_user_partner = request.env.user.partner_id
            if next_item.partner_id.id == current_user_partner.id:
                return "🖊️ You Must Sign"
            else:
                return f"⏳ Waiting: {next_item.partner_id.name}"

        return "⚪ Unknown"

    # -------------------------------
    # Main route
    # -------------------------------
    @http.route('/my/employee/sign', type='http', auth='user', website=True)
    def portal_employee_sign_docs(self, filter="pending", **kwargs):
        user = request.env.user
        SignItem = request.env["sign.request.item"].sudo()

        # Filters
        domain_map = {
            "pending": [('partner_id', '=', user.partner_id.id), ('state', 'in', ('draft', 'sent'))],
            "signed":  [('partner_id', '=', user.partner_id.id), ('state', '=', 'completed')],
            "rejected": [('partner_id', '=', user.partner_id.id), ('state', '=', 'canceled')],
        }

        domain = domain_map.get(filter, domain_map["pending"])
        sign_items = SignItem.search(domain)

        # Build final list for UI
        documents = []
        for item in sign_items:
            sign_request = item.sign_request_id

            documents.append({
                "item": item,
                "filename": sign_request.reference,  # safer than name
                "date": sign_request.create_date.date(),
                "your_status": self._compute_personal_status(item),
                "workflow_status": self._compute_workflow_status(sign_request),
                "access_token": item.access_token,
            })

        # Render
        return request.render("employee_portal_suite.portal_sign_documents_page", {
            "documents": documents,
            "current_filter": filter,
        })
