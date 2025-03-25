from odoo import fields, models, api, exceptions
import datetime


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", selection=[
                              ("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one(
        string="Partner", comodel_name="res.partner", required=True)
    property_id = fields.Many2one(
        string="Property", comodel_name="estate.property", required=True)
    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(
        string="Date Deadline", compute="_compute_date", inverse="_inverse_date")
    property_type_id = fields.Many2one(related="property_id.property_type_id")

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)',
         'Offer price must be strictly positive.')]

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    @api.depends("validity")
    def _compute_date(self):
        for record in self:
            create_date = record.create_date or fields.Datetime.now()
            record.date_deadline = create_date.date() + datetime.timedelta(days=record.validity)

    def _inverse_date(self):
        for record in self:
            record.validity = record.date_deadline.day - record.create_date.day

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def confirm_offer(self):
        for record in self:
            if not record.property_id.offer_ids.filtered(lambda o:  o.status == "accepted"):
                record.status = "accepted"
                record.property_id.selling_price = record.price
                record.property_id.state = 'offer_accepted'
                return True
            raise exceptions.UserError("Only one offer can be accepted.")

    def cancel_offer(self):
        for record in self:
            record.status = "refused"
            record.property_id.selling_price = 0

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------

    @api.model
    def create(self, vals):
        self.env['estate.property'].browse(
            vals['property_id']).state = 'offer_recieved'

        for offer in self.env['estate.property'].browse(vals['property_id']).offer_ids:
            if offer.price > self.price:
                raise exceptions.UserError(
                    "Can't create an offer with a lower amount than an existing offer!")

        return super().create(vals)
