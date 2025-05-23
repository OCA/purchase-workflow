# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import OrderedDict

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "product.mass.addition"]

    def _get_context_add_products(self):
        res = {
            "search_default_filter_to_purchase": 1,
            "search_default_filter_for_current_supplier": 1,
            "quick_access_rights_purchase": 1,
        }
        # Lazy dependency with purchase_stock
        if "picking_type_id" in self._fields:
            res.update(
                {
                    "warehouse": self.picking_type_id.warehouse_id.id,
                    "to_date": self.date_planned,
                }
            )
        return res

    def _get_domain_add_products(self):
        return []

    def add_product(self):
        self.ensure_one()
        res = self._common_action_keys()
        res["context"].update(self._get_context_add_products())
        domain = self._get_domain_add_products()
        if domain:
            res["domain"] = domain
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
        """
        OrderedDict allows to guarantee the correct order
        of the onchanges execution when a new line is
        added to the purchase order and allows to set the
        right price unit depending by qty_to_process and
        min_qty in vendor product pricelist
        """
        return OrderedDict(
            {
                "product_id": None,
                "product_uom": product.quick_uom_id.id,
                "product_qty": product.qty_to_process,
            }
        )

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


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_qty", "product_uom", "company_id")
    def _onchange_quantity(self):
        # Force company_id to po line if not set at the first time
        if not self.company_id and self.order_id:
            self.company_id = self.order_id.company_id
        super(PurchaseOrderLine, self)._onchange_quantity()
