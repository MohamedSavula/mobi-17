from odoo import fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class CentionePo(models.TransientModel):
    _name = 'centione.po'
    _description = 'centione purchase order'

    partner_id = fields.Many2one('res.partner')
    partner_ids = fields.Many2many('res.partner')

    
    def create_po(self):
        for wizard in self:
            purchase_request_line = self.env['centione.purchase.request.line'].browse(self.env.context.get('active_id'))
            product = purchase_request_line.product_id
            orders = []
            for partner in wizard.partner_ids:
                request_vals = {}
                request_vals['partner_id'] = partner.id
                request_vals['origin'] = purchase_request_line.request_id.name
                request_vals['picking_type_id'] = purchase_request_line.picking_type_id.id
                request_vals['delivery_request_line_id'] = purchase_request_line.delivery_request_line_id
                request_vals['initial_mrp_line_id']=purchase_request_line.initial_mrp_line_id
                request_vals['order_line'] = [[0, False,
                                               {'product_id': product.id,
                                                'product_qty': purchase_request_line.qty,
                                                'price_unit': product.standard_price,
                                                'product_uom': purchase_request_line.uom_id.id,
                                                'name': product.display_name,
                                                'date_planned': datetime.today().strftime(
                                                    DEFAULT_SERVER_DATETIME_FORMAT)
                                                }]
                                              ]
                purchase_order = self.env['purchase.order'].create(request_vals)
                orders.append(purchase_order)
            purchase_request_line.purchase_order_ids = [order.id for order in orders]
            purchase_request_line.state = 'done'

            # Check if all lines of the purchase request have been processed
            all_lines = self.env['centione.purchase.request.line'].search([
                ('state', '=', 'draft'), ('request_id', '=', purchase_request_line.request_id.id)])
            if not all_lines:
                purchase_request_line.request_id.state = 'done'
        return {}

class CentionePoLines(models.TransientModel):
    _name = 'centione.po.lines'
    _description = 'centione purchase order'

    def _get_domain(self):
        ids = []
        state = None
        purchase_request_id = self.env.context.get('active_id')
        purchase_request = self.env['centione.purchase.request'].browse(purchase_request_id)
        if self.env.context.get('cancel', False) or self.env.context.get('approve', False):
            state = 'draft'
        elif self.env.context.get('single_po', False):
            state = 'approved'

        for line in purchase_request.purchase_lines_ids:
            if line.state == state:
                ids.append(line.id)
        return [('id', 'in', ids)]

    def _default_purchase_request_id(self):
        return self.env.context.get('active_id')

    purchase_request_id = fields.Integer(string="", required=False,default=_default_purchase_request_id )
    partner_id = fields.Many2one('res.partner')
    partner_ids = fields.Many2many('res.partner')
    purchase_request_lines = fields.Many2many(comodel_name="centione.purchase.request.line",
                                                  string="Purchase Request Line", domain=_get_domain)

    
    def create_po_lines(self):
        for wizard in self:
            # purchase_request_line = self.env['centione.purchase.request.line'].browse(self.env.context.get('active_id'))
            if wizard.purchase_request_lines:
                lines = []
                for purchase_request_line in wizard.purchase_request_lines:
                    product = purchase_request_line.product_id
                    purchase_request_line.state = 'done'
                    lines.append(tuple([0, False,
                                                   {'product_id': product.id,
                                                    'product_qty': purchase_request_line.qty,
                                                    'price_unit': product.standard_price,
                                                    'product_uom': purchase_request_line.uom_id.id,
                                                    'name': product.display_name,
                                                    'date_planned': datetime.today().strftime(
                                                        DEFAULT_SERVER_DATETIME_FORMAT)
                                                    }]))
                orders = []
                for partner in wizard.partner_ids:
                    request_vals = {}
                    request_vals['partner_id'] = partner.id
                    request_vals['origin'] = wizard.purchase_request_lines[0].request_id.name
                    request_vals['picking_type_id'] = wizard.purchase_request_lines[0].picking_type_id.id
                    request_vals['delivery_request_line_id'] = wizard.purchase_request_lines[0].delivery_request_line_id
                    # request_vals['initial_mrp_line_id']=wizard.purchase_request_lines[0].initial_mrp_line_id
                    request_vals['order_line'] = lines
                    purchase_order = self.env['purchase.order'].create(request_vals)
                    orders.append(purchase_order)
                    # purchase_request_line.purchase_order_ids = [order.id for order in orders]


                # Check if all lines of the purchase request have been processed
                all_lines = self.env['centione.purchase.request.line'].search([
                    ('state', '=', 'draft'), ('request_id', '=', purchase_request_line.request_id.id)])
                if not all_lines:
                    purchase_request_line.request_id.state = 'done'
            return {}
