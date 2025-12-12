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

    journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
        required=True,
        domain="[('type','=','general')]"
    )

    def action_create_journal_entry(self):
        for rec in self:

            if rec.state != 'approved':
                raise UserError("Only approved reports can generate a draft journal entry.")

            if rec.journal_entry_id:
                raise UserError("A draft journal entry is already created for this report.")

            if not rec.line_ids:
                raise UserError("No expense lines to post.")

            if not rec.journal_id:
                raise UserError("Please configure a Journal for posting petty cash.")

            if not rec.petty_cash_account_id:
                raise UserError("Please configure the Petty Cash Account.")

            if not rec.input_vat_account_id:
                raise UserError("Please configure the Input VAT Account.")

            # ----------------------
            # GROUP EXPENSES BY CATEGORY
            # ----------------------
            category_groups = {}
            total_vat = 0.0
            total_amount = 0.0

            for line in rec.line_ids:
                # Group amount_before_vat by category account
                account = line.category_id.account_id
                category_groups.setdefault(account, 0.0)
                category_groups[account] += line.amount_before_vat

                # Collect VAT separately
                total_vat += line.vat_amount
                total_amount += line.amount_total

            # ----------------------
            # BUILD MOVE LINES
            # ----------------------
            move_lines = []

            # Debit per category
            for account, amount in category_groups.items():
                move_lines.append((0, 0, {
                    'name': rec.name,
                    'account_id': account.id,
                    'debit': amount,
                    'credit': 0.0,
                }))

            # Debit VAT (if any)
            if total_vat > 0:
                move_lines.append((0, 0, {
                    'name': rec.name + " - VAT",
                    'account_id': rec.input_vat_account_id.id,
                    'debit': total_vat,
                    'credit': 0.0,
                }))

            # Credit Petty Cash Account
            move_lines.append((0, 0, {
                'name': rec.name,
                'account_id': rec.petty_cash_account_id.id,
                'credit': total_amount,
                'debit': 0.0,
            }))

            # ----------------------
            # CREATE DRAFT MOVE
            # ----------------------
            move = self.env['account.move'].create({
                'date': rec.date,
                'ref': rec.name,
                'journal_id': rec.journal_id.id,
                'move_type': 'entry',
                'line_ids': move_lines,
            })

            rec.journal_entry_id = move.id
            rec.message_post(body=f"Draft Journal Entry <b>{move.name}</b> created.")

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': move.id,
                'view_mode': 'form',
            }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        params = self.env['ir.config_parameter'].sudo()

        petty_account = params.get_param('petty_cash_management.petty_cash_account_id')
        vat_account = params.get_param('petty_cash_management.input_vat_account_id')
        journal = params.get_param('petty_cash_management.petty_cash_journal_id')

        if petty_account:
            res['petty_cash_account_id'] = int(petty_account)

        if vat_account:
            res['input_vat_account_id'] = int(vat_account)

        if journal:
            res['journal_id'] = int(journal)

        return res
