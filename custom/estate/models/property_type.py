from odoo import fields, models, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class PropertyType(models.Model):
    _name = 'property.type'
    _description = 'Property Type'

    name = fields.Char('Type')
    property_ids = fields.One2many('estate.property', 'property_id', string='Property')


class PropertyTags(models.Model):
    _name = 'property.tags'
    _description = 'Property Tags'
    _rec_name = 'tags'

    tags = fields.Char('Tags')

    _sql_constraints = [
        ('check_tags', 'UNIQUE (tags)', 'The tags must be unique.'),
     
    ]

class PropertyOffer(models.Model):
    _name = 'property.offer'
    _description = 'Property Offer'

    price = fields.Float('Price')
    status = fields.Selection([
        ('accept', 'Accepted'),
        ('refuse', 'Refused'),
    ], string='Status', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_line = fields.Many2many('estate.property', string='Property')
    validity = fields.Integer('Validity', default=7)
    date_deadline = fields.Date('Deadline', compute='_compute_inverse')  
    offer_id = fields.Many2one('estate.property', string='offer') 
    diff = fields.Float(compute='_compute_diff', string='diff', store=True)
    
    @api.depends('offer_id.expected_price', 'price')
    def _compute_diff(self):
        for rec in self:
            if rec.offer_id.expected_price:
                rec.diff = abs(rec.price - rec.offer_id.expected_price)

    @api.onchange('offer_id.date_availability', 'validity')
    def _compute_inverse(self):
        for rec in self:
            if rec.validity:
                rec.date_deadline = rec.offer_id.date_availability + timedelta(days=rec.validity)
    
    @api.depends('partner_id', 'status', 'offer_id.best_price')
    def button_accept(self):
        for o in self:
            o.ensure_one()
            if o.status == 'accept':
                o.offer_id.costumer_id = o.partner_id
                o.offer_id.selling_price = o.price
        return o.write({'status':'accept'})
                
    def button_refuse(self):
        for o in self:
            o.ensure_one()
            return o.write({'status':'refuse'})
                
    _sql_constraints = [
        ('check_offer_price', 'CHECK(offer >= 0 )', 'The offer price must be strictly positive'),
    ]