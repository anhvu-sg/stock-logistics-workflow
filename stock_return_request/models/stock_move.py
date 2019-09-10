# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_returnable = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        string='Returnable Quantity',
        compute='_compute_qty_returnable',
        readonly=True,
        store=True,
    )

    @api.depends('state', 'returned_move_ids', 'quantity_done',
                 'reserved_availability', 'returned_move_ids.qty_returnable')
    def _compute_qty_returnable(self):
        """Looks for chained returned moves to compute how much quantity
           from the original can be returned """
        for move in self.filtered(lambda x: x.state not in ['draft', 'cancel']):
            if not move.returned_move_ids:
                if move.state == 'done':
                    move.qty_returnable = move.quantity_done
                else:
                    move.qty_returnable = move.reserved_availability
                continue
            move.returned_move_ids._compute_qty_returnable()
            move.qty_returnable = move.quantity_done - sum(
                move.returned_move_ids.mapped('qty_returnable'))
