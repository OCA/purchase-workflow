# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _recalculate_prices(self):
        self.ensure_one()
        if self.state not in ("draft", "sent", "to approve"):
            raise UserError(
                _("Only purchase in the following states can be "
                  "recalculated: 'RFQ', 'To Approve'"))
        price_origin = {rec: (rec.amount_untaxed, rec.amount_tax)
                        for rec in self}
        for line in self.mapped('order_line'):
            vals = line._convert_to_write(line.read()[0])
            line2 = self.env['purchase.order.line'].new(vals)
            # we make this to isolate changed values:
            line2.onchange_product_id()
            line.write({
                'price_unit': line2.price_unit,
                'taxes_id': [(6, 0, line2.taxes_id.ids)],
            })
        self._purchase_price_traceability(price_origin)
        # We return False to prevent our action server
        # to be chained with another empty action server with True value
        return False

    def _purchase_price_traceability(self, origin):
        new = {rec: (rec.amount_untaxed, rec.amount_tax) for rec in self}
        for rec, amount in new.items():
            if amount[0] != origin[rec][0] or amount[1] != origin[rec][1]:
                body = _("Old / New : Untaxed %s / %s ; Taxes %s / %s" % (
                    origin[rec][0], amount[0], origin[rec][1], amount[1]))
                rec.message_post(body=body)
