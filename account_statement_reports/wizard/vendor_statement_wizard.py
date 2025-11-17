from odoo import models, fields

class VendorStatementWizard(models.TransientModel):
    _name = 'vendor.statement.wizard'
    _description = 'Vendor Statement Wizard'
    _inherit = 'statement.mixin'

    def action_print_pdf(self):
        data = self._get_report_data()
        return self.env.ref('account_statement_reports.vendor_statement_pdf').report_action(self, data=data)
