from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EmployeePortalMain(CustomerPortal):

    @http.route('/my/employee', type='http', auth='user', website=True)
    def portal_dashboard(self, **kwargs):
        user = request.env.user
        employee = user.employee_id

        # Only portal employees can access
        if not user.has_group("base.group_portal") or not employee:
            return request.redirect('/my/home')

        # ------------------------------------------------------
        # 1) Employee Requests Count (My Requests)
        # ------------------------------------------------------
        my_request_count = request.env['employee.request'].sudo().search_count([
            ('employee_id', '=', employee.id)
        ])

        # ------------------------------------------------------
        # 2) Material Requests Count (My Materials)
        # ------------------------------------------------------
        my_material_count = request.env['material.request'].sudo().search_count([
            ('employee_id.user_id', '=', user.id)
        ])

        # ------------------------------------------------------
        # 3) Pending Approvals Count (Manager / HR / Finance / CEO)
        # ------------------------------------------------------
        pending_count = 0

        # Manager: ONLY requests where THIS employee is manager_id
        if user.has_group('employee_portal_suite.group_employee_portal_manager'):
            pending_count += request.env['employee.request'].sudo().search_count([
                ('state', '=', 'manager'),
                ('manager_id', '=', employee.id)
            ])

        # HR
        if user.has_group('employee_portal_suite.group_employee_portal_hr'):
            pending_count += request.env['employee.request'].sudo().search_count([
                ('state', '=', 'hr')
            ])

        # Finance
        if user.has_group('employee_portal_suite.group_employee_portal_finance'):
            pending_count += request.env['employee.request'].sudo().search_count([
                ('state', '=', 'finance')
            ])

        # CEO
        if user.has_group('employee_portal_suite.group_employee_portal_ceo'):
            pending_count += request.env['employee.request'].sudo().search_count([
                ('state', '=', 'ceo')
            ])

        # ------------------------------------------------------
        # Render dashboard
        # ------------------------------------------------------
        return request.render("employee_portal_suite.employee_portal_dashboard", {
            "user": user,
            "employee": employee,
            "my_request_count": my_request_count,
            "my_material_count": my_material_count,
            "pending_count": pending_count,
        })

