# -*- coding: utf-8 -*-

from odoo import fields, models


class CategoryApprover(models.Model):
    _name = 'category.approver'

    user_ids = fields.Many2one('res.users')
    department_id = fields.Many2one('category.department', 'Department ', required=True, readonly=False)
    _1st_approver = fields.Boolean("1st Approver", default=False)
    _2st_approver = fields.Boolean("2nd Approver", default=False)
    _3st_approver = fields.Boolean("3rd Approver", default=False)
    _4st_approver = fields.Boolean("4th Approver", default=False)
    _5st_approver = fields.Boolean("5th Approver", default=False)


class ResUsers(models.Model):
    _inherit = 'res.users'

    cate_approver = fields.One2many(comodel_name="category.approver", inverse_name="user_ids",
                                    string="Category Approver", )
