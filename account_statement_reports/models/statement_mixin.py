from odoo import models, fields, api
from datetime import date

class StatementMixin(models.TransientModel):
    _name = 'statement.mixin'
    _description = 'Statement Base Logic'
    _abstract = True

    date_from = fields.Date(required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(required=True, default=fields.Date.today)

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)

    print_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], default='pdf', required=True)

    def _get_lines(self):
        """Fetch account move line entries for the statement."""
        amls = self.env['account.move.line'].search([
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.internal_type', 'in', ['receivable', 'payable']),
        ], order='date asc')

        lines = []
        balance = 0

        for line in amls:
            debit = line.debit
            credit = line.credit
            balance += debit - credit

            lines.append({
                'date': line.date,
                'name': line.move_id.name or line.name,
                'ref': line.move_id.ref,
                'debit': debit,
                'credit': credit,
                'balance': balance,
            })

        return lines

    def _get_report_data(self):
        """Return structured data for report templates."""
        return {
            'partner': self.partner_id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'lines': self._get_lines(),
        }
