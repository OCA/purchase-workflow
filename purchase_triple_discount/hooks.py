def post_init_hook(env):
    env.cr.execute(
        """
        UPDATE purchase_order_line upd
        SET discount1=pol.discount
        FROM (SELECT *
              FROM purchase_order_line
              WHERE discount IS NOT NULL
                AND discount1 IS NULL
                AND discount2 IS NULL
                AND discount3 IS NULL) as pol
        WHERE upd.id = pol.id
    """
    )

    env.cr.execute(
        """
            UPDATE product_supplierinfo upd
            SET discount1=psi.discount
            FROM (SELECT *
                  FROM product_supplierinfo
                  WHERE discount IS NOT NULL
                    AND discount1 IS NULL
                    AND discount2 IS NULL
                    AND discount3 IS NULL) as psi
            WHERE upd.id = psi.id
        """
    )
