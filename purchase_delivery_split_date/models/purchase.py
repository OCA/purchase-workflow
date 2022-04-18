# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from itertools import groupby

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _get_group_keys(self, order, line, picking=False):
        """Define the key that will be used to group. The key should be
        defined as a tuple of dictionaries, with each element containing a
        dictionary element with the field that you want to group by. This
        method is designed for extensibility, so that other modules can add
        additional keys or replace them by others."""
        date = fields.Date.context_today(self.env.user, line.date_planned)
        # Split date value to obtain only the attributes year, month and day
        key = ({"date_planned": fields.Date.to_string(date)},)
        return key

    @api.model
    def _first_picking_copy_vals(self, key, lines):
        """The data to be copied to new pickings is updated with data from the
        grouping key.  This method is designed for extensibility, so that
        other modules can store more data based on new keys."""
        vals = {"move_lines": []}
        for key_element in key:
            if "date_planned" in key_element.keys():
                vals["scheduled_date"] = key_element["date_planned"]
        return vals

    def _get_sorted_keys(self, line):
        """Return a tuple of keys to use in order to sort the order lines.
        This method is designed for extensibility, so that other modules can
        add additional keys or replace them by others."""
        return (line.date_planned,)

    def _create_stock_moves(self, picking):
        """Group the receptions in one picking per group key"""
        moves = self.env["stock.move"]
        # Group the order lines by group key
        order_lines = sorted(
            self.filtered(lambda l: not l.display_type),
            key=lambda l: self._get_sorted_keys(l),
        )
        date_groups = groupby(
            order_lines, lambda l: self._get_group_keys(l.order_id, l, picking=picking)
        )

        first_picking = False
        # If a picking is provided, use it for the first group only
        if picking:
            first_picking = picking
            key, lines = next(date_groups)
            po_lines = self.env["purchase.order.line"]
            for line in list(lines):
                po_lines += line
            picking._update_picking_from_group_key(key)
            moves += super(PurchaseOrderLine, po_lines)._create_stock_moves(
                first_picking
            )

        for key, lines in date_groups:
            # If a picking is provided, clone it for each key for modularity
            if picking:
                copy_vals = self._first_picking_copy_vals(key, lines)
                picking = first_picking.copy(copy_vals)
            po_lines = self.env["purchase.order.line"]
            for line in list(lines):
                po_lines += line
            moves += super(PurchaseOrderLine, po_lines)._create_stock_moves(picking)
        return moves

    def write(self, values):
        res = super().write(values)
        if "date_planned" in values:
            self.mapped("order_id")._check_split_pickings()
        return res

    def create(self, values):
        line = super().create(values)
        if line.order_id.state == "purchase":
            line.order_id._check_split_pickings()
        return line

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        date_planned = self.date_planned
        res = super()._onchange_quantity()
        # preserve the date which was presumably set on the PO line if it is
        # later than the date computed from the Vendor information
        if date_planned and self.date_planned <= date_planned:
            self.date_planned = date_planned
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_split_pickings(self):
        for order in self:
            moves = self.env["stock.move"].search(
                [
                    ("purchase_line_id", "in", order.order_line.ids),
                    ("state", "not in", ("cancel", "done")),
                ]
            )
            pickings = moves.mapped("picking_id")
            pickings_by_date = {}
            for pick in pickings:
                pickings_by_date[pick.scheduled_date.date()] = pick

            order_lines = moves.mapped("purchase_line_id")
            date_groups = groupby(
                order_lines, lambda l: l._get_group_keys(l.order_id, l)
            )
            for key, lines in date_groups:
                date_key = fields.Date.from_string(key[0]["date_planned"])
                for line in lines:
                    for move in line.move_ids:
                        if move.state in ("cancel", "done"):
                            continue
                        if (
                            move.picking_id.scheduled_date.date() != date_key
                            or pickings_by_date[date_key] != move.picking_id
                        ):
                            if date_key not in pickings_by_date:
                                copy_vals = line._first_picking_copy_vals(key, line)
                                new_picking = move.picking_id.copy(copy_vals)
                                pickings_by_date[date_key] = new_picking
                            move._do_unreserve()
                            move.picking_id = pickings_by_date[date_key]
                            move.date_deadline = date_key
                            move._action_assign()
            for picking in pickings:
                if len(picking.move_lines) == 0:
                    picking.write({"state": "cancel"})


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _update_picking_from_group_key(self, key):
        """The picking is updated with data from the grouping key.
        This method is designed for extensibility, so that other modules
        can store more data based on new keys."""
        for rec in self:
            for key_element in key:
                if "date_planned" in key_element.keys():
                    rec.date = key_element["date_planned"]
        return False
