from odoo import models, fields

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'
    _inherit = 'statement.mixin'

    def action_print_pdf(self):
        data = self._get_report_data()
        return self.env.ref('account_statement_reports.customer_statement_pdf').report_action(self, data=data)
