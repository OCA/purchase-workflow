# -*- coding: utf-8 -*-
# © 2016 David Dufresne <david.dufresne@savoirfairelinux.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging


logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    The objective of this hook is to update the field purchase_state in
    existing purchase request lines
    """
    update_field_purchase_state(cr)


def update_field_purchase_state(cr):

    logger.info('Updating field purchase_state on purchase_request_line')

    cr.execute(
        """
        UPDATE purchase_request_line prl
        SET purchase_state = 'approved'
        FROM purchase_request_purchase_order_line_rel AS prpol
        JOIN purchase_order_line AS pol
        ON pol.id = prpol.purchase_order_line_id
        JOIN purchase_order AS po
        ON po.id = pol.order_id
        WHERE prpol.purchase_request_line_id = prl.id
        AND po.state = 'approved'
        """
    )
