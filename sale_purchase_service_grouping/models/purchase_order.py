# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Override.
        #
        # Make odoo think there isn't any existing purchase order to insert the
        # products into.
        #
        # See :meth:`~sale_order_line._purchase_service_create`.
        extra_domain = self.env.context.get("purchase_service_grouping_domain")
        if extra_domain:
            args = expression.AND([args, extra_domain])
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )
