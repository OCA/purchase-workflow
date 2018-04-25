# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from psycopg2.extensions import AsIs
import logging
logger = logging.getLogger(__name__)


def fill_stock_move_created_purchase_request_line(cr):
    logger.info('Adding move_dest_ids to purchase request line.')

    rename = "openupgrade_legacy_11_0_procurement_id"
    cr.execute("""
        UPDATE stock_move as sm
        SET created_purchase_request_line_id = prl.id
        FROM purchase_request_line as prl
        INNER JOIN procurement_order as proc
        ON prl.%s = proc.id
        WHERE proc.move_dest_id = sm.id
    """, (AsIs(rename), ),
    )


def fill_purchase_request_group_id(cr):
    logger.info('Migrating procurement group in purchase request.')

    rename = "openupgrade_legacy_11_0_procurement_id"
    cr.execute("""
        UPDATE purchase_request as pr
        SET group_id = rule.group_id
        FROM purchase_request_line as prl
        INNER JOIN procurement_order as proc
        ON proc.id = prl.%s
        INNER JOIN procurement_group as pg
        ON proc.group_id = pg.id
        INNER JOIN procurement_rule as rule
        ON rule.id = proc.rule_id
        WHERE prl.request_id = pr.id
        AND rule.group_propagation_option = 'fixed'
    """, (AsIs(rename), ),
    )

    cr.execute("""
        UPDATE purchase_request as pr
        SET group_id = pg.id
        FROM purchase_request_line as prl
        INNER JOIN procurement_order as proc
        ON proc.id = prl.%s
        INNER JOIN procurement_group as pg
        ON proc.group_id = pg.id
        INNER JOIN procurement_rule as rule
        ON rule.id = proc.rule_id
        WHERE prl.request_id = pr.id
        AND rule.group_propagation_option = 'propagate'
    """, (AsIs(rename), ),
    )


def fill_purchase_request_line_orderpoint_id(cr):
    logger.info('Migrating purchase request line  in purchase request.')

    rename = "openupgrade_legacy_11_0_procurement_id"
    cr.execute("""
        UPDATE purchase_request_line as prl
        SET orderpoint_id = orderpoint.id
        FROM procurement_order as porder
        INNER JOIN stock_warehouse_orderpoint as orderpoint
        ON orderpoint.id = porder.orderpoint_id
        WHERE prl.%s = porder.id
    """, (AsIs(rename), ),
    )


def migrate(cr, version):
    if not version:
        return
    fill_stock_move_created_purchase_request_line(cr)
    fill_purchase_request_group_id(cr)
    fill_purchase_request_line_orderpoint_id(cr)
