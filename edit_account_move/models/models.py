# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import formatLang


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    project_id = fields.Many2one(comodel_name="project.project", tracking=True)
    sale_id = fields.Many2one(comodel_name="sale.order", tracking=True)
    purchase_custom_id = fields.Many2one(comodel_name="purchase.order", tracking=True)
    account_ids = fields.Many2many(comodel_name="account.account", relation="account_move_account_rel",
                                   column1="account_move_id", column2="account_id",
                                   domain=lambda self: [('id', 'in', self.get_account_ids_from_partner())])
    account_id = fields.Many2one(comodel_name="account.account", domain="[('id', 'in', account_ids)]", tracking=True)
    petty_cash_holder = fields.Boolean(related="partner_id.petty_cash_holder")
    total_withholding = fields.Monetary(store=True, compute='get_total_withholding')
    paid_amount = fields.Monetary(compute='get_paid_amount')
    total_price_withholding = fields.Monetary(compute='get_total_price_withholding')
    total_price_vat = fields.Monetary(compute='get_total_price_vat')
    total_untaxed_amount = fields.Monetary(compute='get_total_untaxed_amount')
    paid_amount_reconcile = fields.Monetary(compute="_compute_payments_widget_reconciled_info")
    comment_note = fields.Char()
    is_accrued = fields.Boolean(copy=False)

    def action_open_business_doc(self):
        self.ensure_one()
        if self.id:
            name = _("Journal Entry")
            res_model = 'account.move'
            res_id = self.id
        elif self.statement_line_id:
            name = _("Bank Transaction")
            res_model = 'account.bank.statement.line'
            res_id = self.statement_line_id.id
        else:
            name = _("Payment")
            res_model = 'account.payment'
            res_id = self.payment_id.id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': res_model,
            'res_id': res_id,
            'target': 'current',
        }

    def action_post(self):
        res = super().action_post()
        for rec in self:
            if rec.ref:
                rec.name = rec.ref
        return res

    @api.onchange('sale_id')
    def _get_sale_line(self):
        for rec in self:
            if rec.sale_id:
                invoice_vals = self.sale_id.with_company(self.sale_id.company_id)._prepare_invoice()
                new_currency_id = self.invoice_line_ids and self.currency_id or invoice_vals.get('currency_id')
                del invoice_vals['company_id']  # avoid recomputing the currency
                if self.move_type == invoice_vals['move_type']:
                    del invoice_vals['move_type']  # no need to be updated if it's same value, to avoid recomputes
                self.update(invoice_vals)
                self.currency_id = new_currency_id
                so_lines = self.sale_id.order_line - self.invoice_line_ids.mapped('sale_line_id')
                for line in so_lines.filtered(lambda l: not l.display_type):
                    self.invoice_line_ids += self.env['account.move.line'].new(
                        line._prepare_invoice_line()
                    )

    @api.constrains('ref')
    def check_ref_uniqe(self):
        for rec in self:
            ref = self.search([('ref', '!=', False), ('ref', '=', rec.ref), ('id', '!=', rec.id),
                               ('partner_id', '=', rec.partner_id.id)])
            if ref and rec.move_type in ('out_invoice', 'in_invoice'):
                raise UserError(_("Bill Reference already exists"))

    @api.depends('amount_total', 'amount_residual')
    def get_paid_amount(self):
        for rec in self:
            rec.paid_amount = rec.amount_total - rec.amount_residual

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_unit')
    def get_total_untaxed_amount(self):
        for rec in self:
            rec.total_untaxed_amount = sum(
                rec.invoice_line_ids.filtered(lambda l: not l.price_withholding).mapped('price_subtotal'))

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_unit')
    def get_total_withholding(self):
        for rec in self:
            rec.total_withholding = sum(
                rec.invoice_line_ids.filtered(lambda l: l.price_withholding > 0).mapped('price_subtotal'))

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_withholding')
    def get_total_price_withholding(self):
        for rec in self:
            rec.total_price_withholding = sum(
                rec.invoice_line_ids.filtered(lambda l: l.account_id.is_withholding).mapped('price_withholding'))

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_unit')
    def get_total_price_vat(self):
        for rec in self:
            rec.total_price_vat = sum(
                rec.invoice_line_ids.filtered(lambda l: not l.account_id.is_withholding).mapped('price_withholding'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                if rec.move_type in ['in_invoice',
                                     'in_refund'] and rec.partner_id.petty_cash_holder and rec.partner_id.journal_id:
                    rec.journal_id = rec.partner_id.journal_id.id
                if rec.move_type in ['in_invoice', 'in_refund']  and not rec.account_id:
                    rec.account_id =rec.account_id.id or rec.partner_id.property_account_payable_id.id
                    rec.account_ids = self.get_account_ids_from_partner()
                elif rec.move_type in ['out_invoice', 'out_refund'] and not rec.account_id:
                    rec.account_id = rec.account_id.id or rec.partner_id.property_account_receivable_id.id
                    rec.account_ids = self.get_account_ids_from_partner()

    @api.onchange('currency_id')
    def onchange_account_currency(self):
        for rec in self:
            rec.account_id = False
            if rec.currency_id.id != self.env.ref('base.EGP').id:
                rec.account_ids = self.get_account_ids_from_partner()
            else:
                if rec.move_type in ['in_invoice', 'in_refund']:
                    rec.account_ids = (self.partner_id.contact_line_ids.filtered(lambda l: not l.is_approved).mapped(
                        'account_id') | rec.partner_id.property_account_payable_id).ids
                elif rec.move_type in ['out_invoice', 'out_refund']:
                    rec.account_ids = (self.partner_id.contact_line_ids.filtered(lambda l: not l.is_approved).mapped(
                        'account_id') | rec.partner_id.property_account_receivable_id).ids

    def get_account_ids_from_partner(self):
        return self.partner_id.contact_line_ids.filtered(lambda l: not l.is_approved).mapped('account_id').ids

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            move.paid_amount_reconcile = move.paid_amount_reconcile
            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.ref:
                        reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False

                    reconciled_vals.append({
                        'name': counterpart_line.name,
                        'journal_name': counterpart_line.journal_id.name,
                        'amount': reconciled_partial['amount'],
                        'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
                        reconciled_partial['currency'].id,
                        'date': counterpart_line.date,
                        'partial_id': reconciled_partial['partial_id'],
                        'account_payment_id': counterpart_line.payment_id.id,
                        'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                        'move_id': counterpart_line.move_id.id,
                        'ref': reconciliation_ref,
                        # these are necessary for the views to change depending on the values
                        'is_exchange': reconciled_partial['is_exchange'],
                        'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
                                                              currency_obj=counterpart_line.company_id.currency_id),
                        'amount_foreign_currency': foreign_currency and formatLang(self.env,
                                                                                   abs(counterpart_line.amount_currency),
                                                                                   currency_obj=foreign_currency)
                    })
                payments_widget_vals['content'] = reconciled_vals
                # new code
                tree_invoice = True
                for paid_amount_reconcile in reconciled_vals:
                    if 'WHtax' not in paid_amount_reconcile.get('ref', False) and 'WTR' not in paid_amount_reconcile.get('ref', False):
                        if self.env.context.get('name_payment') and self.env.context.get('name_payment') in paid_amount_reconcile.get('ref', False):
                            tree_invoice = False
                            move.paid_amount_reconcile += paid_amount_reconcile.get('amount',0)
                if tree_invoice:
                    move.paid_amount_reconcile = move.amount_total - move.amount_residual + move.total_price_withholding
                # end new code
            if payments_widget_vals['content']:
                move.invoice_payments_widget = payments_widget_vals
            else:
                move.invoice_payments_widget = False


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_journal_reconcile = fields.Boolean()


#
# class AccountReconciliationWidget(models.AbstractModel):
#     _inherit = 'account.reconciliation.widget'
#
#     @api.model
#     def _prepare_writeoff_moves(self, move_lines, vals):
#         if 'account_id' not in vals or 'journal_id' not in vals:
#             raise UserError(_("It is mandatory to specify an account and a journal to create a write-off."))
#
#         move_fields = {'journal_id', 'date'}
#         move_vals = {k: v for k, v in vals.items() if k in move_fields}
#
#         company_currency = move_lines.company_id.currency_id
#         currencies = set(line.currency_id for line in move_lines)
#         currency = list(currencies)[0] if len(currencies) == 1 else company_currency
#
#         line_vals = {
#             **{k: v for k, v in vals.items() if k not in move_fields},
#             'partner_id': move_lines[0].partner_id.id,
#             'sequence': 10,
#         }
#
#         if 'debit' not in vals and 'credit' not in vals:
#             balance = -vals.get('balance', 0.0) or sum(move_lines.mapped('amount_residual'))
#         else:
#             balance = vals.get('credit', 0.0) - vals.get('debit', 0.0)
#         line_vals['balance'] = balance
#
#         if currency == company_currency:
#             line_vals['amount_currency'] = balance
#             line_vals['currency_id'] = company_currency.id
#         else:
#             if 'amount_currency' in vals:
#                 line_vals['amount_currency'] = -vals['amount_currency']
#             else:
#                 line_vals['amount_currency'] = sum(move_lines.mapped('amount_residual_currency'))
#             line_vals['currency_id'] = currency.id
#
#         move_vals['line_ids'] = [
#             (0, 0, line_vals),
#             (0, 0, {
#                 'name': _('Write-Off'),
#                 'balance': -line_vals['balance'],
#                 'amount_currency': -line_vals['amount_currency'],
#                 'currency_id': currency.id,
#                 'account_id': move_lines[0].account_id.id,
#                 'partner_id': move_lines[0].partner_id.id,
#                 'sequence': 20,
#             }),
#         ]
#         line = move_lines.filtered(lambda l: l.move_id.move_type != 'entry')
#         if line:
#             line[0].move_id.invoice_line_ids = [(0, 0, {
#                 'name': "Withholding",
#                 'price_withholding': -line_vals['amount_currency'],
#                 'is_price_withholding': True,
#                 'account_id': 258,
#                 'tax_ids': False,
#             })]
#         return move_vals
#
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super()._prepare_invoice_line(**optional_values)
        invoice_line['sale_line_id'] = self.id
        return invoice_line


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    project_id = fields.Many2one(comodel_name="project.project", related="move_id.project_id", store=True)
    sale_id = fields.Many2one(comodel_name="sale.order", related="move_id.sale_id", store=True)
    sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    tax_registration = fields.Char(string="Tax Registration", related="partner_id.vat")
    vat_number = fields.Char(string="Vat Number", related="partner_id.vat_number")
    file_number = fields.Char(string="File Office", related="partner_id.file_number")
    so_po_quantity = fields.Float(compute="get_so_po_qty")
    so_po_remaining = fields.Float(compute="get_so_po_qty")
    account_asset_id = fields.Many2one(comodel_name="account.asset",
                                       domain="[('state', '=', 'model')]")
    is_account_asset = fields.Boolean(copy=False)
    note_custom = fields.Char(string="Note")
    account_ids = fields.Many2many(comodel_name="account.account", relation="account_move_account_rell",
                                   column1="account_move_id", column2="account_id")
    partner_name = fields.Char()
    price_withholding = fields.Float(string="Tax amount")
    is_price_withholding = fields.Boolean(string="", )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        compute='_compute_account_id',
        store=True, readonly=False, precompute=True,
        inverse='_inverse_account_id',
        index=True,
        auto_join=True,
        ondelete="cascade",
        domain="[('id', 'in', account_ids)]",
        check_company=True,
        tracking=True,
    )

    @api.onchange('product_id')
    def get_account_is_accrued(self):
        for rec in self:
            if rec.move_id.is_accrued:
                account_accrued = self.env['account.account'].search([('is_accrued', '=', True)], limit=1)
                if account_accrued:
                    rec.account_id = account_accrued.id

    @api.onchange('product_id', 'account_id')
    def get_analytic_account(self):
        for rec in self:
            if rec.move_id.project_id.analytic_account_id:
                rec.analytic_distribution = {rec.move_id.project_id.analytic_account_id.id: 100.00}

    @api.onchange('price_withholding', 'account_id')
    @api.constrains('price_withholding', 'account_id')
    def get_price_withholding(self):
        for rec in self:
            if rec.parent_state =='posted':
                return True
            if rec.price_withholding and not rec.is_price_withholding:
                if rec.account_id.is_withholding:
                    rec.price_unit = -rec.price_withholding
                else:
                    rec.price_unit = rec.price_withholding

    def _compute_account_id(self):
        res = super()._compute_account_id()
        for rec in self:
            if rec.account_id.id == rec.partner_id.property_account_receivable_id.id or rec.account_id.id == rec.partner_id.property_account_payable_id.id:
                rec.move_id._onchange_partner_id()
                rec.account_id = rec.move_id.account_id.id
        return res

    @api.onchange('analytic_distribution')
    def domain_account_check_analytic(self):
        for rec in self:
            account_ids = [int(account_id) for account_id in rec.analytic_distribution or []]
            accounts = self.env['account.analytic.account'].browse(account_ids)
            domain = [
                ('deprecated', '=', False),
                ('account_type', 'not in', ('asset_receivable', 'liability_payable')),
                ('company_id', '=', rec.move_id.company_id.id)]
            if any(account.state in ['draft', 'in_progres'] for account in
                   accounts.filtered(lambda a: a.project_id)) and rec.move_id.move_type in ['in_invoice', 'in_refund']:
                rec.account_id = False
                domain.append(('is_wib', '=', True))
            elif any(account.state == 'invoiced' for account in
                     accounts.filtered(lambda a: a.project_id)) and rec.move_id.move_type in ['in_invoice',
                                                                                              'in_refund']:
                rec.account_id = False
                domain.append(('is_actual', '=', True))
            rec.account_ids = self.env['account.account'].sudo().search(domain).ids

    @api.onchange('account_asset_id')
    def get_account_asset(self):
        for rec in self:
            if rec.account_asset_id:
                rec.is_account_asset = True
                rec.account_id = rec.account_asset_id.account_asset_id.id
            else:
                rec.is_account_asset = False

    @api.depends('sale_line_ids', 'purchase_line_id', 'product_id')
    def get_so_po_qty(self):
        for rec in self:
            rec.so_po_quantity = rec.so_po_quantity
            rec.so_po_remaining = rec.so_po_remaining
            if rec.sale_line_ids:
                rec.so_po_quantity = sum(rec.sale_line_ids.mapped("product_uom_qty"))
                rec.so_po_remaining = sum(rec.sale_line_ids.mapped("product_uom_qty")) - sum(
                    rec.sale_line_ids.mapped("qty_invoiced"))
            if rec.purchase_line_id:
                rec.so_po_quantity = rec.purchase_line_id.product_qty
                rec.so_po_remaining = rec.purchase_line_id.product_qty - rec.purchase_line_id.qty_invoiced


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['project_id'] = self.project_id.id
        res['sale_id'] = self.id
        return res

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
            if order.currency_id.id == self.env.ref('base.EGP').id:
                order.invoice_ids._onchange_partner_id()
            else:
                order.invoice_ids.onchange_account_currency()


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one(comodel_name="project.project", string="Project", tracking=True)

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['project_id'] = self.project_id.id
        res['purchase_custom_id'] = self.id
        return res

    @api.depends('order_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('order_line.invoice_lines.move_id')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
            if order.currency_id.id == self.env.ref('base.EGP').id:
                order.invoice_ids._onchange_partner_id()
            else:
                order.invoice_ids.onchange_account_currency()
