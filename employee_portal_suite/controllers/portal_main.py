from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EmployeePortalMain(CustomerPortal):

    @http.route('/my', type='http', auth='user', website=True)
    def portal_dashboard(self, **kw):
        user = request.env.user
        employee = user.employee_id

        # -------------------------------
        # 1. My Requests
        # -------------------------------
        my_request_count = request.env['employee.request'].sudo().search_count([
            ('employee_id', '=', employee.id)
        ])

        # -------------------------------
        # 2. Employee Pending Approvals
        # -------------------------------
        employee_pending_count = 0
        pending_recs = request.env['employee.request'].sudo().search([
            ('state', 'in', ['manager', 'hr', 'finance', 'ceo'])
        ])

        for rec in pending_recs:

            if rec.state == 'manager' and user.has_group('employee_portal_suite.group_employee_portal_manager'):
                if rec.manager_id == employee:
                    employee_pending_count += 1

            elif rec.state == 'hr' and user.has_group('employee_portal_suite.group_employee_portal_hr'):
                employee_pending_count += 1

            elif rec.state == 'finance' and user.has_group('employee_portal_suite.group_employee_portal_finance'):
                employee_pending_count += 1

            elif rec.state == 'ceo' and user.has_group('employee_portal_suite.group_employee_portal_ceo'):
                employee_pending_count += 1

        # -------------------------------
        # 3. Material Request Pending Approvals
        # -------------------------------
        if user.has_group('employee_portal_suite.group_mr_purchase_rep'):
            stage = 'purchase'
        elif user.has_group('employee_portal_suite.group_mr_store_manager'):
            stage = 'store'
        elif user.has_group('employee_portal_suite.group_mr_project_manager'):
            stage = 'project_manager'
        elif user.has_group('employee_portal_suite.group_mr_projects_director'):
            stage = 'director'
        elif user.has_group('employee_portal_suite.group_employee_portal_ceo'):
            stage = 'ceo'
        else:
            stage = None

        material_pending_count = 0
        if stage:
            material_pending_count = request.env['material.request'].sudo().search_count([
                ('state', '=', stage)
            ])

        # -------------------------------
        # Render Dashboard
        # -------------------------------
        return request.render("employee_portal_suite.employee_portal_dashboard", {
            "my_request_count": my_request_count,
            "employee_pending_count": employee_pending_count,
            "material_pending_count": material_pending_count,
        })
