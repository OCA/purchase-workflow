# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

import logging
logger = logging.getLogger(__name__)


def update_rejected_requests(cr):
    logger.info('Updating purchase request lines that need to be cancelled.')
    cr.execute("""
        UPDATE purchase_request_line prl
        SET cancelled = true
        FROM purchase_request pr
        WHERE pr.state = 'rejected' AND prl.request_id = pr.id
    """)


def migrate(cr, version):
    if not version:
        return
    update_rejected_requests(cr)
