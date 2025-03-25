from odoo import fields, models, api


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Types"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many(
        comodel_name="estate.property", inverse_name="property_type_id")
    sequence = fields.Integer(string="Sequence", default=1)
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer", inverse_name="property_type_id")
    offer_count = fields.Integer(compute="_compute_offers")

    _sql_constraints = [
        ('unique_property_type_name', 'UNIQUE(name)',
         'Property type name must be unique.')
    ]

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    @api.depends('offer_ids')
    def _compute_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
