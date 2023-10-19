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

    def _get_split_move_by_date_group(self):
        return lambda line: fields.Date.context_today(self.env.user, line.date_planned)

    @api.model
    def _first_picking_copy_vals(self, key, lines):
        """The data to be copied to new pickings is updated with data from the
        grouping key.  This method is designed for extensibility, so that
        other modules can store more data based on new keys."""
        vals = {"move_ids": []}
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
            self._check_split_moves_by_date()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.filtered(
            lambda line: lines.order_id.state == "purchase"
        )._check_split_moves_by_date()
        return lines

    def _compute_price_unit_and_date_planned_and_name(self):
        """
        If the line product quantity is changed and a seller is found,
        the date_planned is updated from the supplier (in _get_date_planned())
        """
        date_planned_by_record = dict()
        for line in self:
            date_planned_by_record[line.id] = line.date_planned
        res = super()._compute_price_unit_and_date_planned_and_name()
        for line in self:
            if (
                date_planned_by_record[line.id]
                and line.date_planned <= date_planned_by_record[line.id]
            ):
                line.date_planned = date_planned_by_record[line.id]
        return res

    def _get_picking_domain_split_by_date(self):
        """
        Don't split pickings that are done or cancel or that have been
        printed.
        """
        return [("state", "not in", ("done", "cancel")), ("printed", "=", False)]

    def _check_split_moves_by_date(self):
        for group_date, lines in self.partition(
            self._get_split_move_by_date_group()
        ).items():
            for picking, moves in lines.move_ids.partition("picking_id").items():
                if not picking.filtered_domain(
                    self._get_picking_domain_split_by_date()
                ):
                    continue
                moves._do_unreserve()
                moves.update(
                    {
                        "date": group_date,
                        "date_deadline": group_date,
                        "picking_id": False,
                    }
                )
                moves.with_context(purchase_delivery_split_date=True)._assign_picking()
                for move in moves:
                    if not move.picking_id.partner_id:
                        move.picking_id.write({"partner_id": picking.partner_id.id})
                moves._action_assign()
                picking.filtered(lambda picking: not picking.move_ids).write(
                    {"state": "cancel"}
                )
