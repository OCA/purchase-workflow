# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Datetime as Dt


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    predicted_arrival_late = fields.Boolean(
        string="Planned to be late",
        compute="_compute_predicted_arrival_late",
        help="True if the arrival at scheduled date is planned to be late. "
        "Takes into account the vendor lead time and the company margin "
        "for lead times.",
    )

    @api.depends("order_id.state")
    def _compute_predicted_arrival_late(self):
        """Colour the lines in red if the products are predicted to arrive
        late."""
        for line in self:
            if line.product_id:
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                )
                order_date = line.order_id.date_order
                po_lead = line.order_id.company_id.po_lead
                delta = po_lead + seller.delay if seller else po_lead
                date_expected = order_date + relativedelta(days=delta)
                line.predicted_arrival_late = (
                    date_expected > line.date_planned and line.order_id.state == "draft"
                )
            else:
                line.predicted_arrival_late = False

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Do not change the scheduled date if we already have one."""
        if self.date_planned:
            return self.date_planned
        else:
            return super(PurchaseOrderLine, self)._get_date_planned(seller, po)

    def action_delayed_line(self):
        raise UserError(
            _(
                "This line is scheduled for: %s. \n However it is now planned to "
                "arrive late."
            )
            % Dt.to_string(Dt.context_timestamp(self, self.date_planned))
        )

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        date_planned = values.get("date_planned")
        if date_planned:
            self = self.filtered(lambda line: line.date_planned == date_planned)
        return super()._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
