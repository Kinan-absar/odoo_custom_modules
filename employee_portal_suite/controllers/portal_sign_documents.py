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
    def _compute_workflow_status(self, sign_request, current_item):
        items = sign_request.request_item_ids.sorted(lambda x: x.sequence)
        user_partner = request.env.user.partner_id

        # Fully signed
        if all(it.state == "completed" for it in items):
            return "🟢 Fully Signed"

        # Rejected by someone
        rejected = next((it for it in items if it.state == "canceled"), None)
        if rejected:
            return f"🔴 Rejected by {rejected.partner_id.name}"

        # Find next signer in sequence who must sign
        next_item = next((it for it in items if it.state != "completed"), None)

        # If this is MY turn
        if next_item and next_item.id == current_item.id:
            return "🖊️ You Must Sign"

        # If I already signed → show next step
        if current_item.state == "completed":
            if next_item:
                return f"⏳ Waiting: {next_item.partner_id.name}"
            return "🟢 Fully Signed"

        # If it's NOT my turn yet → do NOT show who is before me
        return "⏳ Waiting Your Turn"

    # -------------------------------
    # Main route
    # -------------------------------
    @http.route('/my/employee/sign', type='http', auth='user', website=True)
    def portal_employee_sign_docs(self, filter="pending", **kwargs):
        user = request.env.user
        partner = user.partner_id
        SignItem = request.env["sign.request.item"].sudo()

        # Base domain ONLY items belonging to the user
        base_items = SignItem.search([
            ("partner_id", "=", partner.id)
        ])

        documents = []

        for item in base_items:
            req = item.sign_request_id
            items_sorted = req.request_item_ids.sorted(lambda x: x.sequence)

            # RULE: only first pending signer sees the document in "pending"
            first_pending = next((it for it in items_sorted if it.state not in ("completed", "canceled")), None)

            # If it's pending filter → user sees only if they are FIRST PENDING
            if filter == "pending" and first_pending and first_pending.id != item.id:
                continue

            # If not pending filter → show only user's items
            if filter == "signed" and item.state != "completed":
                continue
            if filter == "rejected" and item.state != "canceled":
                continue

            documents.append({
                "item": item,
                "filename": req.reference,
                "date": req.create_date.date(),
                "your_status": self._compute_personal_status(item),
                "workflow_status": self._compute_workflow_status(req, item),
                "access_token": item.access_token,
            })

        return request.render("employee_portal_suite.portal_sign_documents_page", {
            "documents": documents,
            "current_filter": filter,
        })
