from odoo import fields, models, Command


class InheritedEstateProperty(models.Model):
    _inherit = "estate.property"

    def sold_property(self):

        account_move = self.env['account.move'].create({
            'partner_id': self.buyer,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                Command.create(
                    {
                        'name': 'Comisión del 6%',
                        'quantity': 1,
                        'price_unit': self.selling_price * 0.06,
                    }),
                Command.create({
                    'name': 'Gastos administrativos',
                    'quantity': 1,
                    'price_unit': 100.00,
                }
                )
            ]
        })

        return super().sold_property()
