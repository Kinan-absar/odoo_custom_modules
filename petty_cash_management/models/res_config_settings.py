from odoo import models, fields, api

class PettyCashSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Petty Cash Settings"

    petty_cash_account_id = fields.Many2one(
        'account.account',
        string="Petty Cash Account",
        config_parameter='petty_cash_management.petty_cash_account_id'
    )

    input_vat_account_id = fields.Many2one(
        'account.account',
        string="Input VAT Account",
        config_parameter='petty_cash_management.input_vat_account_id'
    )

    petty_cash_journal_id = fields.Many2one(
        'account.journal',
        string="Petty Cash Journal",
        config_parameter='petty_cash_management.petty_cash_journal_id'
    )
