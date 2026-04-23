# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import pytz

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _purchase_split_date_get_group_keys(self, picking):
        """Define the key that will be used to group.

        The key should be defined as a tuple of dictionaries, with each element
        containing a dictionary element with the field that you want to group
        by. This method is designed for extensibility, so that other modules
        can add additional keys or replace them by others.
        """
        tz = self.order_id.picking_type_id.warehouse_id.partner_id.tz
        wh_tz = pytz.timezone(tz) if tz else self.env.tz
        date_planned_tz = self.date_planned.astimezone(pytz.utc).astimezone(wh_tz)
        date = date_planned_tz.date()
        # Split date value to obtain only the attributes year, month and day
        key = (("date_planned", date),)
        return key

    def _purchase_split_date_get_sorted_keys(self):
        """Return a tuple of keys to use in order to sort the order lines.

        This method is designed for extensibility, so that other modules can
        add additional keys or replace them by others.
        """
        return (self.date_planned,)

    def _create_stock_moves(self, picking):
        """Group the receptions in one picking per assignation domain"""
        if not picking:
            # A picking should be provided
            return super()._create_stock_moves(picking)
        moves = self.env["stock.move"]
        tz = picking.picking_type_id.warehouse_id.partner_id.tz
        # Group the order lines by group key
        order_lines = self.filtered(
            lambda line: not line.display_type and line.product_id.type == "consu"
        )
        date_groups = order_lines.grouped(
            lambda line: line._purchase_split_date_get_group_keys(picking),
        )
        for key, po_lines in date_groups.items():
            if (
                not picking.move_ids
                or picking.move_ids == po_lines
                or picking.filtered_domain(
                    picking._purchase_split_date_assign_domain(key, tz)
                )
            ):
                # when the picking is empty or contains all the lines or is
                # valid for the key
                moves += super(PurchaseOrderLine, po_lines)._create_stock_moves(picking)
            else:
                moves_to_assign = super(
                    PurchaseOrderLine, po_lines
                )._create_stock_moves(picking.browse())
                moves_to_assign.with_context(
                    purchase_delivery_split_date=True
                )._assign_picking()
                moves_to_assign._action_confirm()
                moves += moves_to_assign
        return moves

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
