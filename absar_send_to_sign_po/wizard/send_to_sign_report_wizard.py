from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class SendToSignReportWizard(models.TransientModel):
    _name = "send.to.sign.report.wizard"
    _description = "Choose Report to Send for Signing"

    purchase_id = fields.Many2one("purchase.order", required=True)
    report_id = fields.Many2one(
        "ir.actions.report",
        string="Report to Send",
        required=True,
        domain=[('model', '=', 'purchase.order')],
    )

    def action_send(self):
        self.ensure_one()

        if not self.report_id:
            raise UserError("Please select a report.")

        po = self.purchase_id

        # -------------------------
        #  Render the chosen report
        # -------------------------
        pdf_content, _ = self.report_id._render_qweb_pdf(po.ids)
        pdf_b64 = base64.b64encode(pdf_content)

        # -------------------------
        #  Filename
        # -------------------------
        filename = f"{po.name}"
        if po.revision > 0:
            filename += f"_R{po.revision}"
        filename += ".pdf"

        # -------------------------
        #  Create attachment
        # -------------------------
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': pdf_b64,
            'type': 'binary',
            'mimetype': 'application/pdf',
        })

        # -------------------------
        #  Create Sign Template
        # -------------------------
        template = self.env['sign.template'].create({
            'name': f"PO {po.name}",
            'attachment_id': attachment.id,
        })

        po.sign_template_id = template.id
        po.signature_state = "director_pending"
        po.message_post(body=f"PO sent for Director Signature using report: {self.report_id.name}")

        return {
            "type": "ir.actions.act_url",
            "url": f'/odoo/sign/{template.id}/action-sign.Template?id={template.id}&name=Template%20"PO%20{po.name}"',
            "target": "self",
        }
