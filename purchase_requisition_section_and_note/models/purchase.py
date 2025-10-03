from collections import defaultdict

from odoo import Command, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _order = "sequence asc"


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sequence_to_update = fields.Boolean(
        readonly=True,
        help="Technical field to flag orders that have to be sequenced again",
    )

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        res = super()._onchange_requisition_id()
        if self and self.requisition_id:
            lines = []
            for line in self.requisition_id.line_with_sectionnote_ids:
                if line.display_type:
                    lines.append(
                        Command.create(
                            {
                                "product_qty": 0,
                                "display_type": line.display_type,
                                "name": line.name,
                            }
                        )
                    )
            if lines:
                self.order_line = lines
            self._set_sequence_based_on_requisition()
            self.sequence_to_update = True
        return res

    def reorder_lines(self):
        for rec in self:
            rec.sequence_to_update = False

    def _set_sequence_based_on_requisition(self):
        self.ensure_one()
        if self.requisition_id:
            # we apply sequence define in requisition
            data = defaultdict(dict)
            for line in self.requisition_id.line_with_sectionnote_ids:
                data[line.display_type or "no"][line.product_id.name or line.name] = (
                    line.sequence
                )
                # data content is:
                #  {"no": {"my product description": 30},
                #   "line_note": {"my note": 35, "my note2": 37},
                #   "line_section": {"my section": 45}}
            # we need to aggregate already created records
            # with new lines provided by onchange
            for line in self._origin.order_line | self.order_line:
                display = line.display_type or "no"
                sequence = (
                    data.get(display)
                    and data[display].get(
                        line.product_id and line.product_id.name or line.name
                    )
                    or False
                )
                if sequence:
                    line.sequence = sequence
