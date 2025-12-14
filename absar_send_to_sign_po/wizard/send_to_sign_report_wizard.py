from odoo import models, fields, api
import base64

class SendToSignReportWizard(models.TransientModel):
    _name = 'send.to.sign.report.wizard'
    _description = 'Choose Report to Send for Signing'

    purchase_id = fields.Many2one('purchase.order', required=True)

    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        domain="[('model', '=', 'purchase.order')]",
        required=True,
        help="Select which report layout you want to send to sign."
    )

    def action_send(self):
        self.ensure_one()

        # Generate PDF using selected report
        pdf_content, content_type = self.report_id._render_qweb_pdf(self.purchase_id.id)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"{self.purchase_id.name}.pdf",
            'datas': base64.b64encode(pdf_content),
            'type': 'binary',
            'res_model': 'purchase.order',
            'res_id': self.purchase_id.id,
        })

        # Call your Send-to-Sign logic (replace with your real method)
        return self.purchase_id._send_to_sign(attachment)
