# -*- coding: utf-8 -*-
from odoo import models, fields


class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave.type'

    is_legal_leaves = fields.Boolean(copy=False)
    is_unpaid = fields.Boolean(copy=False)
    consume_weekends = fields.Boolean(copy=False)
    is_carried_over = fields.Boolean(copy=False)
    public_holiday = fields.Boolean(copy=False)
    end_service_incentive = fields.Boolean(copy=False)
    apply_double_validation = fields.Boolean(copy=False)
    transfer_from = fields.Boolean(copy=False)
    transfer_to = fields.Boolean(copy=False)
    open_carried_over = fields.Boolean(copy=False)
