from odoo import models, fields, api

class PettyCash(models.Model):
    _name = 'petty.cash'
    _description = 'Petty Cash Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default="/",
        tracking=True
    )

    user_id = fields.Many2one(
        'res.users',
        string="Submitted By",
        default=lambda self: self.env.user,
        tracking=True
    )

    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many(
        'petty.cash.line',
        'petty_cash_id',
        string="Expenses",
    )

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amounts",
        store=True
    )

    amount_vat = fields.Monetary(
        string="VAT",
        compute="_compute_amounts",
        store=True
    )

    amount_total = fields.Monetary(
        string="Total",
        compute="_compute_amounts",
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    journal_entry_id = fields.Many2one(
        'account.move',
        string="Journal Entry",
        readonly=True
    )

    # ------- COMPUTE TOTALS --------
    @api.depends('line_ids.amount_before_vat', 'line_ids.vat_amount', 'line_ids.amount_total')
    def _compute_amounts(self):
        for rec in self:
            rec.amount_untaxed = sum(rec.line_ids.mapped('amount_before_vat'))
            rec.amount_vat = sum(rec.line_ids.mapped('vat_amount'))
            rec.amount_total = sum(rec.line_ids.mapped('amount_total'))
