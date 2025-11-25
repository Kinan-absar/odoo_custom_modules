from odoo import models, fields, api, _
import base64
from odoo.exceptions import UserError

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

    def action_send_to_sign(self):
        """Send PO PDF to director for digital signature."""
        SignRequest = self.env['sign.request']

        for po in self:
            if not po.company_id.project_director_partner_id:
                raise UserError(_("No Project Director configured in settings."))

            # Load signature template (required in Odoo 18)
            template = self.env.ref('absar_send_to_sign_po.po_signature_template')

            # Generate PDF of PO
            pdf_content, dummy = self.env['ir.actions.report']._render_qweb_pdf(
                'purchase.report_purchaseorder',
                po.ids
            )
            pdf_b64 = base64.b64encode(pdf_content)

            # Create sign request for director
            director_request = SignRequest.create({
                'template_id': template.id,
                'reference': f"{po.name} - Director Signature",
                'subject': f"Signature Required for PO {po.name}",

                'request_item_ids': [(0, 0, {
                    'partner_id': po.company_id.project_director_partner_id.id,
                    'mail_sent': True,
                })],

                'attachment_ids': [(0, 0, {
                    'name': f"{po.name}.pdf",
                    'datas': pdf_b64,
                    'res_model': 'sign.request',
                    'res_id': 0,
                })],
            })

            po.director_sign_request_id = director_request.id
            po.signature_state = 'director_pending'


    @api.model
    def _cron_check_signature_workflow(self):
        """Check if director signed → then create CEO request.
           Check if CEO signed → mark PO as fully signed."""
        for po in self.search([('signature_state', '!=', 'signed')]):

            # --- Director finished signing ---
            if po.signature_state == 'director_pending' and \
               po.director_sign_request_id.state == 'completed':

                signed_pdf = po.director_sign_request_id.signed_document
                if not signed_pdf:
                    continue

                if not po.company_id.ceo_partner_id:
                    continue

                SignRequest = self.env['sign.request']
                template = self.env.ref('absar_send_to_sign_po.po_signature_template')

                # Create CEO sign request
                ceo_request = SignRequest.create({
                    'template_id': template.id,
                    'reference': f"{po.name} - CEO Signature",
                    'subject': f"CEO Signature Required for PO {po.name}",

                    'request_item_ids': [(0, 0, {
                        'partner_id': po.company_id.ceo_partner_id.id,
                        'mail_sent': True,
                    })],

                    'attachment_ids': [(0, 0, {
                        'name': f"{po.name}-director-signed.pdf",
                        'datas': signed_pdf,
                        'res_model': 'sign.request',
                        'res_id': 0,
                    })],
                })

                po.ceo_sign_request_id = ceo_request.id
                po.signature_state = 'ceo_pending'


            # --- CEO finished signing ---
            if po.signature_state == 'ceo_pending' and \
               po.ceo_sign_request_id.state == 'completed':

                final_pdf = po.ceo_sign_request_id.signed_document

                if final_pdf:
                    self.env['ir.attachment'].create({
                        'name': f"{po.name}-signed.pdf",
                        'datas': final_pdf,
                        'res_model': 'purchase.order',
                        'res_id': po.id,
                        'type': 'binary',
                    })

                po.signature_state = 'signed'
