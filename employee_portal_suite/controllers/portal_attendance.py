from odoo import http
from odoo.http import request


class EmployeePortalAttendance(http.Controller):

    @http.route('/my/employee/attendance', type='http', auth='user', website=True)
    def attendance_page(self, **kw):
        user = request.env.user

        if not user.has_group('employee_portal_suite.group_employee_portal'):
            return request.redirect('/my')

        return request.render("employee_portal_suite.employee_portal_attendance")



    # ---------------------------
    # Helper
    # ---------------------------
    def _get_employee(self):
        return request.env.user.employee_id

    # ---------------------------
    # Geo Check-In
    # ---------------------------
    @http.route('/geo/checkin', type='json', auth="user", methods=['POST'], csrf=False)
    def geo_checkin(self, **post):
        emp = self._get_employee()
        if not emp or not emp.work_location_id:
            return {"error": "No assigned work location."}

        lat = float(post.get('lat', 0))
        lng = float(post.get('lng', 0))

        allowed_lat = emp.work_location_id.latitude
        allowed_lng = emp.work_location_id.longitude
        max_m = emp.work_location_id.allowed_radius_meters or 200

        geo = request.env['attendance.geo'].sudo().create_geo_checkin(
            employee_id=emp.id,
            lat=lat,
            lng=lng,
            allowed_lat=allowed_lat,
            allowed_lng=allowed_lng,
            max_distance_m=max_m,
        )

        return {
            "message": "Checked in successfully.",
            "attendance_id": geo.id
        }

    # ---------------------------
    # Geo Check-Out
    # ---------------------------
    @http.route('/geo/checkout', type='json', auth="user", methods=['POST'], csrf=False)
    def geo_checkout(self, **post):
        emp = self._get_employee()
        if not emp:
            return {"error": "Employee not found."}

        lat = float(post.get('lat', 0))
        lng = float(post.get('lng', 0))

        open_attendance = request.env['attendance.geo'].sudo().search([
            ('employee_id', '=', emp.id),
            ('state', '=', 'checked_in'),
        ], limit=1)

        if not open_attendance:
            return {"error": "No active check-in."}

        allowed_lat = emp.work_location_id.latitude
        allowed_lng = emp.work_location_id.longitude
        max_m = emp.work_location_id.allowed_radius_meters or 200

        # Check distance out of allowed range
        distance = request.env['attendance.geo']._haversine_distance(
            lat, lng,
            allowed_lat, allowed_lng
        )
        if distance > max_m:
            return {"error": "Out of allowed area."}

        open_attendance.action_checkout(lat, lng)

        return {"message": "Checked out successfully."}
