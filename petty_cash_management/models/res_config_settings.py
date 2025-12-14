from odoo import models, fields, api

class PettyCashConfig(models.Model):
    _name = 'petty.cash.config'
    _description = 'Petty Cash Configuration'

    petty_cash_account_id = fields.Many2one(
        'account.account',
        string="Petty Cash Account",
        required=True
    )
    input_vat_account_id = fields.Many2one(
        'account.account',
        string="Input VAT Account",
        required=True
    )
    petty_cash_journal_id = fields.Many2one(
        'account.journal',
        string="Petty Cash Journal",
        domain="[('type','=','general')]",
        required=True
    )

    @api.model
    def get_singleton(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({})
        return config
