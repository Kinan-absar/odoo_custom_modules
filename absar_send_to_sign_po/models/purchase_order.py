from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    signature_state = fields.Selection([
        ('draft', 'Not Sent'),
        ('director_pending', 'Waiting Director Signature'),
        ('ceo_pending', 'Waiting CEO Signature'),
        ('signed', 'Fully Signed'),
    ], default='draft', tracking=True)

    director_sign_request_id = fields.Many2one('sign.request', string="Director Sign Request")
    ceo_sign_request_id = fields.Many2one('sign.request', string="CEO Sign Request")
