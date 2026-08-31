# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from datetime import date, datetime

from odoo import api, fields, models

from .res_company import SORTING_CRITERIA, SORTING_DIRECTION

# Neutral value used as sorting key when a line has no value for the selected
# criteria, so empty values are sorted first in ascending order and we never
# compare values of different types.
EMPTY_SORT_VALUES = {
    "boolean": False,
    "char": "",
    "date": date.min,
    "datetime": datetime.min,
    "float": 0.0,
    "html": "",
    "integer": 0,
    "monetary": 0.0,
    "selection": "",
    "text": "",
}


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    line_order = fields.Selection(
        selection=SORTING_CRITERIA,
        string="Sort Lines By",
        default=lambda self: self.env.company.default_po_line_order,
    )
    line_direction = fields.Selection(
        selection=SORTING_DIRECTION,
        string="Sort Direction",
        default=lambda self: self.env.company.default_po_line_direction,
    )

    @api.onchange("line_order")
    def onchange_line_order(self):
        if not self.line_order:
            self.line_direction = False

    def _get_line_sort_key(self, line):
        """Resolve the sorting criteria into a comparable value."""
        self.ensure_one()
        value = line
        field = None
        for subfield in self.line_order.split("."):
            field = value._fields[subfield]
            value = value[subfield]
        if isinstance(value, models.BaseModel):
            value = value.display_name or ""
        elif value is False or value is None:
            value = EMPTY_SORT_VALUES.get(field.type, "")
        return value

    def _get_line_sort_chunks(self):
        """Split the order lines in chunks of consecutive sortable lines.

        Section, subsection and note lines are pinned to their current place,
        so the lines are only sorted inside the block they belong to.
        """
        self.ensure_one()
        chunks = []
        sortable = self.env["purchase.order.line"]
        # Lines created in the same write are appended at the end of the
        # cached one2many, so we can't rely on the recordset order here: we
        # need the real one, the same the user sees in the list (_order).
        for line in self.order_line.sorted(lambda line: (line.sequence, line.id)):
            if line.display_type:
                if sortable:
                    chunks.append((True, sortable))
                    sortable = self.env["purchase.order.line"]
                chunks.append((False, line))
            else:
                sortable |= line
        if sortable:
            chunks.append((True, sortable))
        return chunks

    def _sort_purchase_line(self):
        sorted_orders = self.browse()
        for order in self:
            if not order.line_order:
                continue
            reverse = order.line_direction == "desc"
            sequence = 0
            for sortable, lines in order._get_line_sort_chunks():
                if sortable:
                    lines = lines.sorted(key=order._get_line_sort_key, reverse=reverse)
                for line in lines:
                    sequence += 10
                    if line.sequence == sequence:
                        continue
                    line.sequence = sequence
            sorted_orders |= order
        # The cached one2many isn't invalidated when the sequence of the lines
        # changes, so it would keep serving the order the lines had before
        # being sorted. It could happen when we are not in the purchase context.
        sorted_orders.invalidate_recordset(["order_line"])

    def write(self, values):
        res = super().write(values)
        if {"order_line", "line_order", "line_direction"} & values.keys():
            self._sort_purchase_line()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        purchases = super().create(vals_list)
        purchases._sort_purchase_line()
        return purchases


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.order_id._sort_purchase_line()
        return lines
