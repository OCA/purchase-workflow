# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """The purchase order form always required an order type, so every
    existing company keeps requiring it. A fresh install does not.
    """
    if not version:
        return
    cr.execute("UPDATE res_company SET purchase_order_type_required = TRUE")
