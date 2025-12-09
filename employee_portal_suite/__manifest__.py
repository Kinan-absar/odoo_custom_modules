{
    'name': 'Employee Portal Suite',
    'version': '1.0',
    'summary': 'Employee & Material Requests, GPS Attendance, Multi-Level Approvals, Employee Portal Suite',

    'description': """
    Comprehensive Employee Portal Suite providing a full service system for employees, managers, and administrators.

    Features Included:

    ✔ Employee Portal (/my/employee)
    ✔ Clean custom portal layout and navigation
    ✔ Employee Requests workflow (Employee → Manager → HR → Finance → CEO)
    ✔ Material Requests workflow (Employee → Purchase Rep → Store Manager → Project Manager → Director → CEO)
    ✔ Full approval timeline visible in backend + portal
    ✔ Manager Approvals Center with tabs (Employee / Material)
    ✔ Dynamic Request Submission Forms
    ✔ Request Detail Pages with approval history and comments
    ✔ Automatic request numbering (ERQ / MR sequences)
    ✔ PDF reports for all request types
    ✔ GPS Attendance with geofencing (Check-In / Check-Out)
    ✔ Automatic checkout cron for missed attendance
    ✔ Work location GPS configuration per employee
    ✔ Backend menus for Requests, Attendance, and Material Requests
    ✔ Secure access using custom portal user, manager, HR, finance, and approval groups
    ✔ Completely isolated portal permissions (employees only see their own records)

    This module enables a complete self-service environment for employees and a unified approval center for managers.
    """,

    'author': 'Kinan',
    'category': 'Human Resources',
    'application': True,
    'installable': True,

    # ------------------------------------------------------------------
    #  DEPENDENCIES
    # ------------------------------------------------------------------
    'depends': [
        'base',
        'web',
        'portal',
        'hr',
        'mail',
        'hr_attendance',
        'website',
        'purchase',
    ],

    # ------------------------------------------------------------------
    #  DATA FILES LOADED IN ORDER
    # ------------------------------------------------------------------
    'data': [
        # --- SECURITY ---
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        # --- DATA / SEQUENCES ---
        'data/request_sequence.xml',
        'data/attendance_cron.xml',

        # --------------------------------------------------
        # REPORTS
        # --------------------------------------------------
        'reports/report_action.xml',
        'reports/report_employee_request.xml',
        'reports/report_material_request.xml',

        # --- BACKEND VIEWS ---
        'views/employee_request_views.xml',
        'views/material_request_views.xml',
        'views/attendance_views.xml',
        'views/menus.xml',
        'views/work_location_inherit.xml',
        
        # --------------------------------------------------
        # EMPLOYEE PORTAL (FRONTEND)
        # --------------------------------------------------
        'views/employee_portal_layout.xml',
        'views/employee_dashboard_page.xml',

        # Employee Requests
        'views/employee_requests_page.xml',
        'views/employee_request_detail_page.xml',
        'views/employee_request_new_form.xml',

        # Attendance Page
        'views/employee_attendance_page.xml',

        # --------------------------------------------------
        # MATERIAL REQUEST PORTAL (FRONTEND)
        # --------------------------------------------------
        'views/employee_material_requests_page.xml',
        'views/employee_material_request_detail_page.xml',
        'views/employee_material_request_new_form.xml',

        # --------------------------------------------------
        # MANAGER PORTAL (APPROVALS)
        # --------------------------------------------------
        'views/portal_material_approval_detail.xml',
        'views/portal_employee_approvals_list.xml',
        'views/portal_material_approvals_list.xml',
        'views/portal_manager_request_detail.xml',
        'views/portal_sign_documents.xml',

    ],

    # ------------------------------------------------------------------
    #  ASSETS (JS)
    # ------------------------------------------------------------------
    'assets': {
        'web.assets_frontend': [
            "employee_portal_suite/static/src/js/sign_redirect.js",
            'employee_portal_suite/static/src/js/attendance_geo.js',
        ],
    },
    'images': ['static/description/icon.png'],

}
