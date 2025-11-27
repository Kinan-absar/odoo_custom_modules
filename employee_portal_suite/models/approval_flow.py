from odoo import models, fields

class ApprovalFlow(models.Model):
    _name = "employee.approval.flow"
    _description = "Approval Flow"

    name = fields.Char()
