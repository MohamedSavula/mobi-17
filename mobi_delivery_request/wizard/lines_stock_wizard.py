# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

LOGGER = logging.getLogger(__name__)


class LinesStockWizard(models.TransientModel):
    _name = 'lines.stock.wizard'

    def _get_domain(self):
        ids = []
        delivery_request_id = self.env.context.get('active_id')
        delivery_request = self.env['centione.delivery.request'].browse(delivery_request_id)
        for line in delivery_request.delivery_lines_ids:
            if line.state == 'warehouse_review':
                ids.append(line.id)
        return [('id', 'in', ids)]

    location_id = fields.Many2one('stock.location', "Source Location", required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location", required=True)
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse")
    employee = fields.Many2one('hr.employee')
    delivery_request_line_ids = fields.Many2many(comodel_name="centione.delivery.request.line",
                                                 string="Delivery Request Lines", domain=_get_domain)

    
    def create_centione_transfer(self):
        self.ensure_one()
        picking_type_id = int(self.env['ir.config_parameter'].sudo().get_param('picking_type_first_id')) or False
        if picking_type_id:
            lines_vals = []
            for delivery_request_line in self.delivery_request_line_ids:
                lines_vals.append(tuple([0, False, {
                    'date_expected': fields.Datetime.now(),
                    'product_uom': delivery_request_line.uom_id.id,
                    'product_id': delivery_request_line.product_id.id,
                    'name': delivery_request_line.product_id.name,
                    'picking_type_id': picking_type_id,
                    'product_uom_qty': delivery_request_line.qty - delivery_request_line.requested_amount,
                    'state': 'draft'
                }]))
                delivery_request_line.broker_warehouse = self.location_dest_id.id
                delivery_request_line.requested_amount = delivery_request_line.qty
                delivery_request_line.state = 'requested'
            if self.delivery_request_line_ids:
                values = {
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'move_type': 'one',
                    'picking_type_id': picking_type_id,
                    'picking_type_code': 'internal',
                    'priority': '1',
                    'state': 'draft',
                    'origin': self.delivery_request_line_ids[0].request_id.name,
                    'min_date': fields.Datetime.now(),
                    'name': '/',
                    'analytic_account_id': self.delivery_request_line_ids[0].request_id.analytic_account_id.id,
                    # 'delivery_request_line_id': delivery_request_line.id,
                    'move_lines': lines_vals
                }
                picking = self.env['stock.picking'].create(values)
                picking.action_confirm()

            return True
        else:
            raise ValidationError("There Is No 'Picking Type' Assigned To The Warehouse Of Source Location")

    
    def create_centione_purchase(self):
        self.ensure_one()
        self.create_centione_transfer()
        self.create_or_modify_line('normal')
        return {}

    def create_or_modify_line(self, line_type):
        del_request_line = self.env['centione.delivery.request.line'].browse(self.env.context.get('active_id'))
        purchase_request = self.env['centione.purchase.request'].search([('state', '=', 'open'),('delivery_request_id','=',del_request_line.id)], limit=1)
        if self.delivery_request_line_ids:
            picking_type_id = int(self.env['ir.config_parameter'].sudo().get_param('picking_type_purchase_id')) or False
            if not purchase_request:
                lines = []
                for delivery_request_line in self.delivery_request_line_ids:
                    delivery_request_line.state = 'purchase_request'
                    lines.append(tuple([0, False, {'product_id': delivery_request_line.product_id.id,
                                                   'cost_price': delivery_request_line.product_id.standard_price,
                                                   'delivery_request_line_id': delivery_request_line.id,
                                                   'qty': delivery_request_line.qty,
                                                   'uom_id': delivery_request_line.uom_id.id,
                                                   'state': 'draft',
                                                   'type': line_type,
                                                   'picking_type_id': picking_type_id,
                                                   'notes': delivery_request_line.notes}]))
                request_vals = {
                    'origin': del_request_line.request_id.name,
                    'purchase_lines_ids': lines
                }
                purchase_request = self.env['centione.purchase.request'].create(request_vals)
            else:
                # Check if there is already opened line for this product in the open purchase request lines
                for delivery_request_line in self.delivery_request_line_ids:
                    delivery_request_line.state = 'purchase_request'
                    for purchase_line in purchase_request.purchase_lines_ids:
                        if purchase_line.product_id.id == delivery_request_line.product_id.id \
                                and purchase_line.type == line_type and purchase_line.state != 'done' \
                                and purchase_line.uom_id.id == delivery_request_line.uom_id.id \
                                and purchase_line.picking_type_id.id == picking_type_id:
                            purchase_line.qty += delivery_request_line.qty
                            break
                    # if there wasn't any open lines, create new one
                    request_line_values = {
                        'product_id': delivery_request_line.product_id.id,
                        'cost_price': delivery_request_line.product_id.standard_price,
                        'qty': delivery_request_line.qty,
                        'uom_id': delivery_request_line.uom_id.id,
                        'state': 'draft',
                        'notes': delivery_request_line.notes,
                        'request_id': purchase_request.id,
                        'type': line_type,
                        'picking_type_id': picking_type_id
                    }
                self.env['centione.purchase.request.line'].create(request_line_values)
            context = dict(self.env.context)
            context.update({'employee_used_case': self.employee.work_email})
            template = self.env.ref('mobi_delivery_request.mail_purchase_request_created_notification')
            template.with_context(context).sudo().send_mail(purchase_request.id, force_send=True)
            return True
