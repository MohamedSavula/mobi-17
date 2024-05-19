# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class BoardMember(models.Model):
    _name = 'board.member'

    board_member_ids = fields.One2many("board.member.line", 'board_member_id')
    done = fields.Boolean()
    social_insurance_s_date = fields.Date(string="social insurance start date", required=False, )
    title = fields.Char(string="", required=False, )

    def _default_year(self):
        today = datetime.today()
        current_year = today.year
        return str(current_year)

    def _get_year_selection(self):
        _year_selection = [('2015', '2015'), ('2016', '2016'), ('2017', '2017')]
        today = datetime.today()
        current_year = today.year
        year = 2018
        while year <= current_year:
            _year_selection.append((str(year), str(year)))
            year += 1
        return _year_selection

    name = fields.Selection(string="Year", selection=_get_year_selection, default=_default_year, required=True, )

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(BoardMember, self).copy({'name': '2015'})
        vals = [(0, 0, {'name': line.name, 'amount': line.amount}) for line in self.board_member_ids]
        res.update({'board_member_ids': vals})
        return res

    @api.constrains('name')
    def check_name(self):
        records = self.env['board.member'].search([('id', '!=', self.id), ('name', '=', self.name)])
        if records:
            raise ValidationError(_("Year Must Be Unique"))

    def unlink(self):
        for rec in self:
            if rec.done:
                raise ValidationError(_("You Can Not Delete This Record"))
            else:
                return super(BoardMember, rec).unlink()


class BoardMemberLine(models.Model):
    _name = 'board.member.line'

    name = fields.Char(required=True)
    amount = fields.Float(required=True)
    board_member_id = fields.Many2one('board.member', ondelete="cascade")
    opex_cogs = fields.Selection([('opex', 'Opex'), ('cogs', 'Cogs')])
