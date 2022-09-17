from contextlib import nullcontext
from operator import index
from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _name = 'estate.property'
    # _inherit = 'res.partner'
    _description = 'Estate Property'
    
    three_months_after = datetime.now() + relativedelta(months=3)
    

    name = fields.Char('Name', required = True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date',copy=False,default=three_months_after, help="please do reservation in 3 months")
    expected_price = fields.Float('Expected Price', required = True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedroom(s)', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades (sqm)')
    garage = fields.Boolean('Garage')  
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection([
        ('n', 'North'),
        ('s', 'South'),
        ('e', 'East'),
        ('w', 'West')
    ], string='Garden Orientation')
    active = fields.Boolean('Active')
    state = fields.Selection([
        ('new', 'New'),
        ('recieved', 'Offer Recieved'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string='State', required=True, default='new')
    property_type_id = fields.Many2one('property.type', string='Property Type')
    property_tags_line = fields.Many2many('property.tags')
    costumer_id = fields.Many2one('res.partner', string='Buyer')
    sales_id = fields.Many2one('res.users', string='Salesman')
    offer_ids = fields.One2many('property.offer', inverse_name='offer_id',  string='Price')

    @api.depends('total_area', 'garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends('expected_price', 'offer_ids.price')
    def _compute_best_price(self):
        if self.offer_ids.price != False:
            for record in self:
                lists = [{'diff' : abs(rec.price - record.expected_price), 'price' : rec.price} for rec in record.offer_ids]
                lists = sorted(lists, key = lambda k : k['diff'])
                record.best_price = lists[0]['price']
        else:
            self.best_price = 0
    
    total_area = fields.Integer('Total Area (sqm)', readonly=True, compute='_compute_total_area')
    best_price = fields.Integer('Best Price', readonly=True, compute='_compute_best_price')
    property_id = fields.Many2one('property.type', string='Property')

    def button_recieve(self):
        self.ensure_one()
        return self.write({'state':'recieved'})

    def button_accept(self):
        self.ensure_one()
        return self.write({'state':'accepted'})
    
    def button_sold(self):
        self.ensure_one()
        if self.state == 'canceled':
           raise UserError('Canceled properties cannot be sold.')
        return self.write({'state':'sold'})

    def button_cancel(self):
        self.ensure_one() #ini buat supaya tidak terjadi error/ rewrite data
        return self.write({'state':'canceled'})

    
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0 )', 'The expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0 )', 'The selling price must be strictly positive'),
    ]
