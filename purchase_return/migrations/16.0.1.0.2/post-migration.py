from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_return_order_line
        SET display_type = NULL
        WHERE display_type = 'product'
        """,
    )
