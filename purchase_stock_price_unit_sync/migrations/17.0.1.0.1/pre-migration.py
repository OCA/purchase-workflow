# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if env["ir.module.module"].search(
        [("name", "=", "product_cost_price_avco_sync"), ("state", "=", "installed")]
    ):
        # Delete adjustment svl's when product_cost_price_avco_sync is installed
        openupgrade.logged_query(
            env.cr,
            "DELETE FROM stock_valuation_layer WHERE account_move_id IS NOT NULL",
        )
