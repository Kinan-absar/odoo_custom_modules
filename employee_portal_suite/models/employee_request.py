from odoo import models, fields, api

class EmployeeRequest(models.Model):
    _name = "employee.request"
    _description = "Employee Request"

    name = fields.Char()
