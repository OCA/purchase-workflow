# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Import company and settings *before* the purchase section: else, at
# installation, Odoo will init ``purchase.order.category_qty_split_by_uom``
# using its default value; but its default value is computed through a method
# that uses company's field ``res.company.po_category_qty_split_by_uom``, which
# is not initialized yet
from . import res_company
from . import res_config_settings

# Import this file before importing purchase files, else Odoo will try to fill
# the ``purchase.order.line.qty_by_product_category_id`` field by creating
# ``purchase.order.qty.by.product.category`` records before the model is
# initialized
from . import purchase_order_qty_by_product_category

# Import purchase files for last
from . import purchase_order
from . import purchase_order_line
