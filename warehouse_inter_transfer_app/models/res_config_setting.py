# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approve_by_manager = fields.Boolean("Approve By Manager",related="company_id.approve_by_manager" ,readonly=False)


class ResCompany(models.Model):
    _inherit = "res.company"

    approve_by_manager = fields.Boolean("Approve By Manager")
