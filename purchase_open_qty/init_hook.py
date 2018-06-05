# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging


logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    store_field_qty_to_receive_and_invoice(cr)


def store_field_qty_to_receive_and_invoice(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order_line' AND
    column_name='qty_to_receive'""")
    if not cr.fetchone():
        logger.info('Creating field qty_to_receive on purchase_order_line')
        cr.execute(
            """
            ALTER TABLE purchase_order_line ADD COLUMN qty_to_receive float;
            COMMENT ON COLUMN purchase_order_line.qty_to_receive IS
            'Qty to Receive';
            """)

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order_line' AND
    column_name='qty_to_invoice'""")
    if not cr.fetchone():
        logger.info('Creating field qty_to_invoice on purchase_order_line')
        cr.execute(
            """
            ALTER TABLE purchase_order_line ADD COLUMN qty_to_invoice float;
            COMMENT ON COLUMN purchase_order_line.qty_to_invoice IS
            'Qty to Bill';
            """)

    logger.info('Computing values for fields qty_to_receive and qty_to_invoice'
                ' on purchase_order_line')
    cr.execute(
        """
        UPDATE purchase_order_line pol
        SET qty_to_invoice = pol.qty_received - pol.qty_invoiced
        FROM product_product p
        JOIN product_template t ON p.product_tmpl_id = t.id
        WHERE t.purchase_method = 'receive' AND pol.product_id = p.id
        """
    )
    cr.execute(
        """
        UPDATE purchase_order_line pol
        SET qty_to_invoice = pol.product_qty - pol.qty_invoiced
        FROM product_product p
        JOIN product_template t ON p.product_tmpl_id = t.id
        WHERE t.purchase_method != 'receive' AND pol.product_id = p.id
        """
    )
    cr.execute(
        """
        UPDATE purchase_order_line
        SET qty_to_receive = pol.qty
        FROM (SELECT purchase_line_id, sum(product_uom_qty) as qty
              FROM stock_move
              WHERE purchase_line_id IS NOT NULL AND
                  state not in ('cancel', 'done')
              GROUP BY purchase_line_id) as pol
        WHERE purchase_order_line.id = pol.purchase_line_id
        """
    )
