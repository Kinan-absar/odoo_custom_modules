from odoo import http
from odoo.http import request


class EmployeePortalRequests(http.Controller):

    # ---------------------------------------------------------
    # Helper
    # ---------------------------------------------------------
    def _get_employee(self):
        return request.env.user.employee_id

    # ---------------------------------------------------------
    # EMPLOYEE — LIST OWN REQUESTS
    # ---------------------------------------------------------
    @http.route('/my/employee/requests', type='http', auth='user', website=True)
    def portal_list(self, **kw):
        emp = self._get_employee()
        if not emp:
            return request.redirect('/my')

        requests = request.env['employee.request'].sudo().search([
            ('employee_id', '=', emp.id)
        ])

        return request.render("employee_portal_suite.employee_requests_page", {
            "requests": requests,
        })

    # ---------------------------------------------------------
    # EMPLOYEE — VIEW SINGLE REQUEST
    # ---------------------------------------------------------
    @http.route('/my/employee/requests/<int:req_id>', type='http', auth='user', website=True)
    def portal_detail(self, req_id, **kw):
        emp = self._get_employee()
        rec = request.env['employee.request'].sudo().browse(req_id)

        if not emp or rec.employee_id != emp:
            return request.redirect('/my')

        return request.render("employee_portal_suite.employee_request_detail_page", {
            "request_rec": rec,
        })

    # ---------------------------------------------------------
    # EMPLOYEE — NEW FORM
    # ---------------------------------------------------------
    @http.route('/my/employee/requests/new', type='http', auth='user', website=True)
    def portal_new(self, **kw):
        emp = self._get_employee()
        if not emp:
            return request.redirect('/my')

        return request.render("employee_portal_suite.employee_request_new_form")

    # ---------------------------------------------------------
    # EMPLOYEE — CREATE REQUEST
    # ---------------------------------------------------------
    @http.route('/my/employee/requests/create', type='http', auth='user', website=True, csrf=True)
    def portal_create(self, **post):
        emp = self._get_employee()
        if not emp:
            return request.redirect('/my')

        # Clean mapping
        mapping = {
            "leave": "leave",
            "housing": "housing",
            "advance": "advance",
            "travel": "travel",
            "training": "training",
            "medical": "medical",
            "vacation_settlement": "vacation_settlement",
            "asset": "asset",
            "letter": "letter",
            "bank": "bank",
            "transfer": "transfer",
            "exit": "exit",
            "other": "other",
        }
        req_type = mapping.get(post.get("request_type"), "other")

        # Build vals
        vals = {
            'employee_id': emp.id,
            'request_date': post.get('request_date'),
            'request_type': req_type,
            'description': post.get('description'),
        }

        # Leave fields
        if req_type == "leave":
            vals['leave_from'] = post.get('leave_from') or False
            vals['leave_to']   = post.get('leave_to') or False

        new_rec = request.env['employee.request'].sudo().create(vals)
        # Auto-submit the request (no backend user needed)
        new_rec.sudo().action_submit()
        return request.redirect(f"/my/employee/requests/{new_rec.id}")


    # ---------------------------------------------------------
    # MANAGER — APPROVAL LIST
    # ---------------------------------------------------------
    @http.route('/my/employee/approvals', type='http', auth='user', website=True)
    def portal_approvals(self, **kw):
        user = request.env.user

        # Only portal managers/HR/Finance/CEO can see this
        if not (
            user.has_group("employee_portal_suite.group_employee_portal_manager")
            or user.has_group("employee_portal_suite.group_employee_portal_hr")
            or user.has_group("employee_portal_suite.group_employee_portal_finance")
            or user.has_group("employee_portal_suite.group_employee_portal_ceo")
        ):
            return request.redirect('/my')

        employee = user.employee_id
        filtered = []

        # search all requests in approval pipeline
        requests = request.env['employee.request'].sudo().search([
            ('state', 'in', ['manager', 'hr', 'finance', 'ceo'])
        ])

        for req in requests:

            # manager stage
            if req.state == 'manager' and req.manager_id == employee and user.has_group('employee_portal_suite.group_employee_portal_manager'):
                filtered.append(req)

            # HR stage
            if req.state == 'hr' and user.has_group('employee_portal_suite.group_employee_portal_hr'):
                filtered.append(req)

            # Finance stage
            if req.state == 'finance' and user.has_group('employee_portal_suite.group_employee_portal_finance'):
                filtered.append(req)

            # CEO stage
            if req.state == 'ceo' and user.has_group('employee_portal_suite.group_employee_portal_ceo'):
                filtered.append(req)

        return request.render("employee_portal_suite.portal_employee_approvals_list", {
            "requests": filtered,
        })


    # ---------------------------------------------------------
    # MANAGER — APPROVAL DETAIL
    # ---------------------------------------------------------
    @http.route('/my/employee/approvals/<int:req_id>', type='http', auth='user', website=True)
    def portal_approval_detail(self, req_id, **kw):
        user = request.env.user
        rec = request.env['employee.request'].sudo().browse(req_id)

        if not rec.exists():
            return request.redirect('/my')

        # Only managers/hr/finance/ceo
        if not (
            user.has_group("employee_portal_suite.group_employee_portal_manager")
            or user.has_group("employee_portal_suite.group_employee_portal_hr")
            or user.has_group("employee_portal_suite.group_employee_portal_finance")
            or user.has_group("employee_portal_suite.group_employee_portal_ceo")
        ):
            return request.redirect('/my')

        return request.render("employee_portal_suite.portal_manager_request_detail", {
            "request_rec": rec
        })

   # ---------------------------------------------------------
# PORTAL APPROVE (Manager / HR / Finance / CEO)
# ---------------------------------------------------------
    @http.route('/my/employee/requests/approve', type='http', auth='user', website=True, csrf=True)
    def portal_approve(self, **post):
        req_id = int(post.get("req_id"))
        comment = post.get("comment") or ""
        user = request.env.user

        rec = request.env['employee.request'].sudo().browse(req_id)

        if not rec.exists():
            return request.redirect('/my/employee/approvals')

        if rec.state == "manager":
            rec.manager_comment = comment
            rec.action_manager_approve()

        elif rec.state == "hr":
            rec.hr_comment = comment
            rec.action_hr_approve()

        elif rec.state == "finance":
            rec.finance_comment = comment
            rec.action_finance_approve()

        elif rec.state == "ceo":
            rec.ceo_comment = comment
            rec.action_ceo_approve()


        return request.redirect('/my/employee/approvals')


        # ---------------------------------------------------------
    # PORTAL REJECT (Manager / HR / Finance / CEO)
    # ---------------------------------------------------------
    @http.route('/my/employee/requests/reject', type='http', auth='user', website=True, csrf=True)
    def portal_reject(self, **post):
        req_id = int(post.get("req_id"))
        comment = (post.get("comment") or "").strip()
        user = request.env.user

        # REQUIRE REJECTION COMMENT
        if not comment:
            return request.redirect(f"/my/employee/requests/{req_id}")  # go back to detail page

        rec = request.env['employee.request'].sudo().browse(req_id)

        if not rec.exists():
            return request.redirect('/my/employee/approvals')

        # Save rejection comment in correct field
        if rec.state == 'manager' and rec.manager_id == user.employee_id:
            rec.manager_comment = comment

        elif rec.state == 'hr' and user.has_group('employee_portal_suite.group_employee_portal_hr'):
            rec.hr_comment = comment

        elif rec.state == 'finance' and user.has_group('employee_portal_suite.group_employee_portal_finance'):
            rec.finance_comment = comment

        elif rec.state == 'ceo' and user.has_group('employee_portal_suite.group_employee_portal_ceo'):
            rec.ceo_comment = comment

        # Now actually reject
        rec.sudo().action_reject()

        return request.redirect('/my/employee/approvals')
    