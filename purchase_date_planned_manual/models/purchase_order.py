# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _compute_predicted_arrival_late(self):
        """Colour the lines in red if the products are predicted to arrive
        late."""
        for line in self:
            seller = line.product_id._select_seller(
                line.product_id,
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and
                line.order_id.date_order[:10],
                uom_id=line.product_uom)
            order_date = datetime.strptime(line.order_id.date_order,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
            po_lead = line.order_id.company_id.po_lead
            delta = po_lead + seller.delay if seller else po_lead
            date_expected = (order_date + relativedelta(days=delta)).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)
            line.predicted_arrival_late = (
                date_expected > line.date_planned and line.order_id.state ==
                'draft')

    predicted_arrival_late = fields.Boolean(
        string='Planned to be late',
        compute=_compute_predicted_arrival_late,
        help='True if the arrival at scheduled date is planned to be late. '
             'Takes into account the vendor lead time and the company margin '
             'for lead times.')

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Do not change the scheduled date if we already have one."""
        if self.date_planned:
            return datetime.strptime(
                self.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            return super(PurchaseOrderLine, self)._get_date_planned(seller, po)

    @api.multi
    def action_delayed_line(self):
        raise UserError(_('This line is scheduled for: %s. \n However it is '
                          'now planned to arrive late.') % self.date_planned)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _inverse_date_planned(self):
        """WARNING: This overwrites a standard method.
        This is done because we don't want to change the scheduled date for
        the PO lines in any scenario."""
        pass
