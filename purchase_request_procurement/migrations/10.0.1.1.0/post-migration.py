# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

import logging
logger = logging.getLogger(__name__)


def fill_purchase_request_group_id(cr):
    logger.info('Migrating procurement group in purchase request.')

    cr.execute("""
        UPDATE purchase_request as pr
        SET group_id = rule.group_id
        FROM purchase_request_line as prl
        INNER JOIN procurement_order as proc
        ON proc.id = prl.procurement_id
        INNER JOIN procurement_group as pg
        ON proc.group_id = pg.id
        INNER JOIN procurement_rule as rule
        ON rule.id = proc.rule_id
        WHERE prl.request_id = pr.id
        AND rule.group_propagation_option = 'fixed'
    """)

    cr.execute("""
        UPDATE purchase_request as pr
        SET group_id = pg.id
        FROM purchase_request_line as prl
        INNER JOIN procurement_order as proc
        ON proc.id = prl.procurement_id
        INNER JOIN procurement_group as pg
        ON proc.group_id = pg.id
        INNER JOIN procurement_rule as rule
        ON rule.id = proc.rule_id
        WHERE prl.request_id = pr.id
        AND rule.group_propagation_option = 'propagate'
    """)


def migrate(cr, version):
    if not version:
        return
    fill_purchase_request_group_id(cr)
