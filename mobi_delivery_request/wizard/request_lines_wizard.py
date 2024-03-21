from odoo import fields, models


class PurchaseRequestWizard(models.TransientModel):
    _name = 'purchase.request.wizard'

    date_to = fields.Date(string="Date To", required=True, )
    date_from = fields.Date(string="Date From", required=True, )
