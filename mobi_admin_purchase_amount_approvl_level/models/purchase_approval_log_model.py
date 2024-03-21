from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PurchaseReviewLogModel(models.Model):
    _name = "purchase.review.log"
    _rec_name = 'user_id'
    review_status = fields.Selection([('1st_approve', '1st Approved'),
                                      ('draft', 'RFQ'),
                                      ('sent', 'RFQ Sent'),
                                      ('1st_approve', '1st Approved'),
                                      ('2nd_approve', '2nd Approved'),
                                      ('3rd_approve', '3rd Approved'),
                                      ('4th_approve', '4th Approved'),
                                      ('5th_approve', '5th Approved'),
                                      ('to approve', 'To Approve'),
                                      ('purchase', 'Purchase Order'),
                                      ('done', 'Locked'),
                                      ('cancel', 'Cancelled')], string='Review Status')
    user_id = fields.Many2one('res.users', string='User')
    order_id = fields.Many2one('purchase.order')
    date = fields.Datetime(string="Date")
    job_position = fields.Char()
