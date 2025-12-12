from odoo import models, fields, api
from odoo.exceptions import UserError

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

    # ---------------------------
    # WORKFLOW ACTIONS
    # ---------------------------

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError("You cannot submit a petty cash report with no expense lines.")
            if rec.state != 'draft':
                raise UserError("Only drafts can be submitted.")
            rec.state = 'submitted'
            rec.message_post(body="Petty Cash Report submitted for approval.")

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError("Only submitted reports can be approved.")
            rec.state = 'approved'
            rec.message_post(body="Petty Cash Report approved.")

    def action_refuse(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError("Only submitted reports can be refused.")
            rec.state = 'refused'
            rec.message_post(body="Petty Cash Report was refused.")

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state not in ['refused', 'approved']:
                raise UserError("Only refused or approved reports can be reset to draft.")
            rec.state = 'draft'
            rec.message_post(body="Petty Cash Report moved back to draft.")

    def action_create_journal_entry(self):
        """ Temporary placeholder, real logic will be added in Step 7 """
        for rec in self:
            if rec.state != 'approved':
                raise UserError("Only approved reports can generate a draft journal entry.")

            # Placeholder message
            rec.message_post(body="Draft Journal Entry will be generated in the next step.")
        return True

    def write(self, vals):
        for rec in self:
            if rec.state not in ['draft'] and any(field in vals for field in ['line_ids', 'name', 'date']):
                raise UserError("You cannot modify a petty cash report unless it is in Draft state.")
        return super(PettyCash, self).write(vals)
