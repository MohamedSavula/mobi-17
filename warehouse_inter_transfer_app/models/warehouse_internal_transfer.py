# -*- coding: utf-8 -*-

from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

# inter warehouse transfer line
class ProductOperations(models.Model):
	_name = "product.operations"
	_description = "Product Operations"

	product_id = fields.Many2one('product.product')
	demand_qty = fields.Float(default=1.0)
	inter_war_trans_id = fields.Many2one('inter.tranfer')

# inter Warehouse transfer main
class InterTransfer(models.Model):
	_name = 'inter.tranfer'
	_description = "Inter Transfer"
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
	_mail_post_access = 'read'
	_order = 'id desc'

	is_picking = fields.Boolean()
	approve_by_manager = fields.Boolean(string="Approve by Manager",related="company_id.approve_by_manager")
	picking_ids = fields.Many2many('stock.picking','inter_picking_default_rel','inter_war_id','picking_id',"Picking",copy=False)
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company, index=True)
	state = fields.Selection([('draft','Draft'),('approve','Approved'),('waiting','Waiting'),('cancel','Cancel'),('done','Done')],default='draft', string='State')
	name = fields.Char(string='Transfer Reference', required=True, default='New', copy=False, readonly=True)
	partner_id = fields.Many2one('res.partner', required=True)
	picking_type_id = fields.Many2one('stock.picking.type',required=True)
	location_id = fields.Many2one('stock.location', "Source Location",required=True,domain ="[('usage','=', 'internal')]")
	location_dest_id = fields.Many2one('stock.location',"Destination Location",required=True,domain = "[('usage', '=', 'internal')]")
	transit_location_id = fields.Many2one('stock.location',required=True,domain = "[('usage', '=', 'internal')]")
	product_opt_ids = fields.One2many('product.operations','inter_war_trans_id')
	internal_note = fields.Text()
	is_generate = fields.Boolean()

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('inter.tranfer') or 'New'
		res = super(InterTransfer, self).create(vals)
		if res.company_id.approve_by_manager and res.state == 'draft':
			res.write({'is_generate':False})
		if not res.company_id.approve_by_manager and res.state == 'draft':
			res.write({'is_generate':True})
		return res

	def approve_transfer(self):
		if not self.product_opt_ids:
			raise ValidationError(_("Please define products or operations lines...!"))
		if self.company_id.approve_by_manager and self.env.user.has_group('stock.group_stock_manager'):
			self.write({'state':'approve'})
		if self.company_id.approve_by_manager and self.state == 'approve':
			self.write({'is_generate':True})

	def cancel_transfer(self):
		self.write({'state':'cancel','is_generate':False})
		if self.picking_ids:
			self.picking_ids.action_cancel()

	def generate_internal_transfer(self):
		if not self.product_opt_ids:
			raise ValidationError(_("Please define products or operations lines...!"))
		picking_list=[]
		vals = {
			'scheduled_date' : datetime.now(),
			'picking_type_id': self.picking_type_id.id,
			'location_id': self.location_id.id,
			'location_dest_id': self.transit_location_id.id,
			'move_type': 'direct',
			'inter_war_tr_id' : self.id,
			'origin' : self.name,
			'name' : self.picking_type_id.sudo().sequence_id.next_by_id()
		}

		pick_id=self.env['stock.picking'].sudo().create(vals)
		for line in self.product_opt_ids :
			mv = self.env['stock.move'].sudo().create({
				'name': line.product_id.display_name,
				'product_uom': line.product_id.uom_id.id,
				'picking_id': pick_id.id,
				'picking_type_id': self.picking_type_id.id,
				'product_id': line.product_id.id,
				'product_uom_qty': abs(line.demand_qty),
				'state': 'draft',
				'location_id': self.location_id.id,
				'location_dest_id': self.transit_location_id.id,
			})

			mvl = self.env['stock.move.line'].sudo().create({
				'picking_id':pick_id.id,
				'location_id':pick_id.location_id.id,
				'location_dest_id':pick_id.location_dest_id.id,
				'qty_done': line.demand_qty,
				'product_id': line.product_id.id,
				'move_id':mv.id,
				'product_uom_id':line.product_id.uom_id.id,
			})
		pick_id.sudo().action_confirm()
		picking_list.append(pick_id.id)
		
		# create second transfer
		values = {
			'scheduled_date' : datetime.now(),
			'picking_type_id': self.picking_type_id.id,
			'location_id': self.transit_location_id.id,
			'location_dest_id': self.location_dest_id.id,
			'move_type': 'direct',
			'inter_war_tr_id' : self.id,
			'origin' : self.name,
			'name' : self.picking_type_id.sudo().sequence_id.next_by_id()
		}
		picking2 = self.env['stock.picking'].sudo().create(values)

		for line in self.product_opt_ids :
			mv = self.env['stock.move'].sudo().create({
				'name': line.product_id.display_name,
				'product_uom': line.product_id.uom_id.id,
				'picking_id': picking2.id,
				'picking_type_id': self.picking_type_id.id,
				'product_id': line.product_id.id,
				'product_uom_qty': abs(line.demand_qty),
				'state': 'draft',
				'location_id': self.transit_location_id.id,
				'location_dest_id': self.location_dest_id.id,
			})

			mvl = self.env['stock.move.line'].sudo().create({
				'picking_id':picking2.id,
				'location_id':picking2.location_id.id,
				'location_dest_id':picking2.location_dest_id.id,
				'qty_done': line.demand_qty,
				'product_id': line.product_id.id,
				'move_id':mv.id,
				'product_uom_id':line.product_id.uom_id.id,
			})

		picking2.sudo().action_confirm()
		picking_list.append(picking2.id)
		if pick_id.state in ('confirmed','assigned')  or picking2.state in ('confirmed','assigned'):
			self.write({'state':'waiting'})
		self.write({'is_generate':False,'is_picking':True,'picking_ids':[(6,0,picking_list)]})

	def action_view_generated_transfer(self):
		picking = self.env['stock.picking'].search([('id','in',self.picking_ids.ids)])
		action = self.env.ref('stock.action_picking_tree_all').read()[0]
		if picking:
			action['domain'] = [('id', 'in', picking.ids)]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	def unlink(self):
		if self.env.user.has_group('stock.group_stock_manager'):
			return super(InterTransfer, self).unlink()
		else:
			raise ValidationError(_("Delete access have only for Inventory Manager..!"))


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	inter_war_tr_id = fields.Many2one("inter.tranfer",string="Inter Warehouse Transfer",readonly=True)

	def button_validate(self):
		res = super(StockPicking,self).button_validate()
		pickings = self.env['stock.picking'].search([('inter_war_tr_id', '=', self.inter_war_tr_id.id)])
		if all(pick.state == 'done' for pick in pickings):
			self.inter_war_tr_id.write({'state':'done'})
		return res
