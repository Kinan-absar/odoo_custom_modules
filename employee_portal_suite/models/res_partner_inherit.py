from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_portal_employee = fields.Boolean()
