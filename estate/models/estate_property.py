from odoo import fields, models, api, exceptions
from odoo.tools.float_utils import float_compare
import datetime


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Properties"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Availability Date", copy=False, default=fields.Date.today() + datetime.timedelta(days=90))
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(
        string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Number of Facades")
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area (sqm)")
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_recieved', 'Offer Recieved'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        string="State",
        default="new",
        copy=False,
        required=True
    )
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        string="Garden Orientation"
    )
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one(comodel_name="estate.property.type")
    buyer = fields.Many2one(comodel_name="res.partner", copy=False)
    salesperson = fields.Many2one(
        comodel_name="res.users", default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name="estate.property.tag")
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer", inverse_name="property_id")
    total_area = fields.Integer(compute="_compute_area")
    best_offer = fields.Float(compute="_compute_price")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'Expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'Selling price must be positive.'),
    ]

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    @api.depends('living_area', 'garden_area')
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_price(self):
        for record in self:
            best_price = 0
            for offer_id in record.offer_ids:
                if (offer_id.price > best_price):
                    best_price = offer_id.price
            record.best_offer = best_price

    @api.onchange("garden")
    def _on_change_garden(self):
        self.garden_area = 10 if self.garden else 0
        self.garden_orientation = "north" if self.garden else None

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if not record.offer_ids.filtered(lambda o:  o.status == "accepted"):
                return
            if (float_compare(value1=record.selling_price, value2=record.expected_price * 0.9, precision_digits=1) == -1):
                raise exceptions.UserError(
                    f"The selling price must be at least 90% of the expected expected price.")

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def sold_property(self):
        for record in self:
            if record.state == "cancelled":
                raise exceptions.UserError(
                    "Canceled properties cannot be sold.")
            record.state = "sold"
            return True

    def cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise exceptions.UserError(
                    "Sold properties cannot be cancelled.")
            record.state = "cancelled"
            return True

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------
    @api.ondelete(at_uninstall=False)
    def _unlink_estate_property(self):
        for record in self:
            if (record.state not in ('new', 'cancelled')):
                raise exceptions.UserError(
                    "Can't delete a estate property in this state !")
