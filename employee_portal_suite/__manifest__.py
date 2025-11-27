{
    "name": "Employee Portal Suite",
    "version": "1.0.0",
    "summary": "Employee portal with requests, approvals, and geo-attendance.",
    "author": "Kinan",
    "category": "Human Resources",
    "depends": ["base", "portal", "hr", "hr_attendance", "website"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",

        "views/menus.xml",
        "views/employee_request_views.xml",
        "views/approval_views.xml",
        "views/attendance_views.xml",
        "views/portal_templates.xml",
    ],
    "installable": True,
    "application": True,
}
