# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    store_field_qty_to_receive_and_invoice(env)


def store_field_qty_to_receive_and_invoice(env):
    env.cr.execute(
        """SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order_line' AND
    column_name='qty_to_receive'"""
    )
    if not env.cr.fetchone():
        logger.info("Creating field qty_to_receive on purchase_order_line")
        env.cr.execute(
            """
            ALTER TABLE purchase_order_line ADD COLUMN qty_to_receive float;
            COMMENT ON COLUMN purchase_order_line.qty_to_receive IS
            'Qty to Receive';
            """
        )

    env.cr.execute(
        """SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order_line' AND
    column_name='qty_to_invoice'"""
    )
    if not env.cr.fetchone():
        logger.info("Creating field qty_to_invoice on purchase_order_line")
        env.cr.execute(
            """
            ALTER TABLE purchase_order_line ADD COLUMN qty_to_invoice float;
            COMMENT ON COLUMN purchase_order_line.qty_to_invoice IS
            'Qty to Bill';
            """
        )

    logger.info(
        "Computing values for fields qty_to_receive and qty_to_invoice"
        " on purchase_order_line"
    )
    env.cr.execute(
        """
        UPDATE purchase_order_line pol
        SET qty_to_invoice = pol.qty_received - pol.qty_invoiced
        FROM product_product p
        JOIN product_template t ON p.product_tmpl_id = t.id
        WHERE t.purchase_method = 'receive' AND pol.product_id = p.id
        """
    )
    env.cr.execute(
        """
        UPDATE purchase_order_line pol
        SET qty_to_invoice = pol.product_qty - pol.qty_invoiced
        FROM product_product p
        JOIN product_template t ON p.product_tmpl_id = t.id
        WHERE t.purchase_method != 'receive' AND pol.product_id = p.id
        """
    )
    env.cr.execute(
        """
        UPDATE purchase_order_line pol
        SET qty_to_receive =
            CASE
                WHEN pt.type = 'service' THEN pol.product_qty - pol.qty_received
                ELSE (
                    SELECT COALESCE(SUM(sm.product_uom_qty), 0)
                    FROM stock_move sm
                    WHERE sm.purchase_line_id = pol.id
                      AND sm.state NOT IN ('cancel', 'done')
                )
            END
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE pp.id = pol.product_id
        """
    )
