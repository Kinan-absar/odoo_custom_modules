# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EmployeePortalSignDocs(CustomerPortal):

    # -------------------------------
    # Personal status
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
    # Workflow: respecting signing order
    # -------------------------------
    def _compute_workflow_status(self, sign_request):
        items = sign_request.request_item_ids

        # Fully signed
        if all(it.state == "completed" for it in items):
            return "🟢 Fully Signed"

        # Rejected
        canceled = next((it for it in items if it.state == "canceled"), None)
        if canceled:
            name = canceled.partner_id.name or "Unknown"
            return f"🔴 Rejected by {name}"

        # Correct signing order using signer_sequence
        items_sorted = items.sorted(lambda x: x.signer_sequence or 0)

        # find next signer
        next_item = next((it for it in items_sorted if it.state != "completed"), None)

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
        partner = user.partner_id
        SignItem = request.env["sign.request.item"].sudo()

        # Base: only user’s requests
        base_items = SignItem.search([
            ("partner_id", "=", partner.id)
        ])

        documents = []

        for item in base_items:
            req = item.sign_request_id

            # FIXED: use signer_sequence
            items_sorted = req.request_item_ids.sorted(lambda x: x.signer_sequence or 0)

            # FIRST pending signer
            first_pending = next(
                (it for it in items_sorted if it.state not in ("completed", "canceled")),
                None
            )

            # Show only user's turn in Pending
            if filter == "pending":
                if not first_pending or first_pending.id != item.id:
                    continue

            # Signed filter
            if filter == "signed" and item.state != "completed":
                continue

            # Rejected filter
            if filter == "rejected" and item.state != "canceled":
                continue

            documents.append({
                "item": item,
                "filename": req.reference,
                "date": req.create_date.date(),
                "your_status": self._compute_personal_status(item),
                "workflow_status": self._compute_workflow_status(req),  # FIXED
                "access_token": item.access_token,
            })

        return request.render("employee_portal_suite.portal_sign_documents_page", {
            "documents": documents,
            "current_filter": filter,
        })
