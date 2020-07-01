# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "product.mass.addition"]

    @api.multi
    def add_product(self):
        self.ensure_one()
        res = self._common_action_keys()
        res["context"].update(
            {
                "search_default_filter_to_purchase": 1,
                "search_default_filter_for_current_supplier": 1,
            }
        )
        commercial = self.partner_id.commercial_partner_id.name
        res["name"] = "🔙 %s (%s)" % (_("Product Variants"), commercial)
        res["view_id"] = (
            self.env.ref("purchase_quick.product_tree_view4purchase").id,
        )
        res["search_view_id"] = (
            self.env.ref("purchase_quick.product_search_view4purchase").id,
        )
        return res

    def _get_quick_line(self, product):
        return self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("order_id", "=", self.id)],
            limit=1,
        )

    def _get_quick_line_qty_vals(self, product):
        return {"product_qty": product.qty_to_process}

    def _complete_quick_line_vals(self, vals, lines_key=""):
        return super(PurchaseOrder, self)._complete_quick_line_vals(
            vals, lines_key="order_line"
        )

    def _add_quick_line(self, product, lines_key=""):
        return super(PurchaseOrder, self)._add_quick_line(
            product, lines_key="order_line"
        )
