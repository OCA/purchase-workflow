# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "product.mass.addition"]

    def add_product(self):
        self.ensure_one()
        res = self._common_action_keys()
        res["context"].update(
            {
                "search_default_filter_to_purchase": 1,
                "search_default_filter_for_current_supplier": 1,
                "quick_access_rights_purchase": 1,
            }
        )
        commercial = self.partner_id.commercial_partner_id.name
        res["name"] = "🔙 {} ({})".format(_("Product Variants"), commercial)
        res["view_id"] = (self.env.ref("purchase_quick.product_tree_view4purchase").id,)
        res["search_view_id"] = (
            self.env.ref("purchase_quick.product_search_form_view").id,
        )
        return res

    def _get_quick_line(self, product):
        result = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("order_id", "=", self.id)]
        )
        nr_lines = len(result.ids)
        if nr_lines > 1:
            raise ValidationError(
                _(
                    "Must have only 1 line per product for mass addition, but "
                    "there are %s lines for the product %s"
                    % (nr_lines, product.display_name),
                )
            )
        return result

    def _get_quick_line_qty_vals(self, product):
        return {
            "product_qty": product.qty_to_process,
            "product_uom": product.quick_uom_id.id,
        }

    def _complete_quick_line_vals(self, vals, lines_key=""):
        # This params are need for playing correctly the onchange
        vals.update(
            {
                "order_id": self.id,
                "partner_id": self.partner_id.id,
            }
        )
        return super(PurchaseOrder, self)._complete_quick_line_vals(
            vals, lines_key="order_line"
        )

    def _add_quick_line(self, product, lines_key=""):
        return super(PurchaseOrder, self)._add_quick_line(
            product, lines_key="order_line"
        )
