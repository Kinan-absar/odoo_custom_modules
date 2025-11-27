from odoo import models, fields

class AttendanceGeo(models.Model):
    _name = "attendance.geo"
    _description = "Geo Attendance"

    name = fields.Char()
