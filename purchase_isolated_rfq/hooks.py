# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


def post_init_hook(cr, registry):
    """ Set value for order_sequence on old records """
    cr.execute(
        """
        update purchase_order
        set order_sequence = true
        where state not in ('draft', 'cancel')
        """
    )
