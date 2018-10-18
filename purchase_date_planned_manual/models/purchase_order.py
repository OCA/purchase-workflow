# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Datetime as Dt


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    predicted_arrival_late = fields.Boolean(
        string='Planned to be late',
        compute='_compute_predicted_arrival_late',
        help='True if the arrival at scheduled date is planned to be late. '
             'Takes into account the vendor lead time and the company margin '
             'for lead times.')

    @api.multi
    def _compute_predicted_arrival_late(self):
        """Colour the lines in red if the products are predicted to arrive
        late."""
        for line in self:
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and
                line.order_id.date_order[:10],
                uom_id=line.product_uom)
            order_date = fields.Datetime.from_string(line.order_id.date_order)
            po_lead = line.order_id.company_id.po_lead
            delta = po_lead + seller.delay if seller else po_lead
            date_expected = fields.Datetime.to_string(
                order_date + relativedelta(days=delta))
            line.predicted_arrival_late = (
                date_expected > line.date_planned and line.order_id.state ==
                'draft')

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Do not change the scheduled date if we already have one."""
        if self.date_planned:
            return fields.Datetime.from_string(self.date_planned)
        else:
            return super(PurchaseOrderLine, self)._get_date_planned(seller, po)

    @api.multi
    def action_delayed_line(self):
        raise UserError(_(
            'This line is scheduled for: %s. \n However it is now planned to '
            'arrive late.') % Dt.to_string(Dt.context_timestamp(
                self, Dt.from_string(self.date_planned))))
