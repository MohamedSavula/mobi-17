# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import OperationalError, Error

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    force_date = fields.Datetime('Force Date')

#     def migrate_moves(self):
#         moves = self.env['stock.move.line'].search([])
#         for move in moves:
#             move.write({'date': move.move_id.date})
#
#
# class StockMove(models.Model):
#     _inherit = "stock.move"
#
#     def _action_done(self):
#         res = super(StockMove, self)._action_done()
#         for move in self:
#             if res[0].picking_id.force_date:
#                 res.write({'date': res[0].picking_id.force_date})
#                 stock_move_line = self.env['stock.move.line'].search([('move_id', '=', move.id)])
#                 for obj in stock_move_line:
#                     obj.write({'date': res[0].picking_id.force_date})
#
#         return res
#
#     def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
#         self.ensure_one()
#         AccountMove = self.env['account.move']
#         quantity = self.env.context.get('forced_quantity', self.product_qty)
#         quantity = quantity if self._is_in() else -1 * quantity
#
#         # Make an informative `ref` on the created account move to differentiate between classic
#         # movements, vacuum and edition of past moves.
#         ref = self.picking_id.name
#         if self.env.context.get('force_valuation_amount'):
#             if self.env.context.get('forced_quantity') == 0:
#                 ref = 'Revaluation of %s (negative inventory)' % ref
#             elif self.env.context.get('forced_quantity') is not None:
#                 ref = 'Correction of %s (modification of past move)' % ref
#
#         move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value),
#                                                                                   credit_account_id, debit_account_id)
#         if move_lines:
#             if self.picking_id.force_date:
#                 date = datetime.strptime(str(self.picking_id.force_date), '%Y-%m-%d %H:%M:%S')
#             else:
#                 date = self._context.get('force_period_date', fields.Date.context_today(self))
#             new_account_move = AccountMove.sudo().create({
#                 'journal_id': journal_id,
#                 'line_ids': move_lines,
#                 'date': date,
#                 'ref': ref,
#                 'stock_move_id': self.id,
#             })
#             new_account_move.post()
