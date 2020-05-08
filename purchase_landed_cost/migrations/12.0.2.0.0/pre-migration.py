# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    # Force delete old `product_price_unit` field as the name will be reused
    # to rename `standard_price_old`
    env.ref(
        "purchase_landed_cost.field_purchase_cost_distribution_line__product_price_unit"
    ).with_context({"_force_unlink": True}).unlink()

    openupgrade.rename_fields(
        env,
        [
            (
                "purchase.cost.distribution.line",
                "purchase_cost_distribution_line",
                "standard_price_old",
                "product_price_unit",
            ),
            (
                "purchase.cost.distribution.line",
                "purchase_cost_distribution_line",
                "total_amount",
                "product_price_amount",
            ),
            (
                "purchase.cost.distribution.line",
                "purchase_cost_distribution_line",
                "standard_price_new",
                "landed_cost_unit",
            ),
            (
                "purchase.cost.distribution.line",
                "purchase_cost_distribution_line",
                "cost_ratio",
                "expense_unit",
            ),
            (
                "purchase.cost.distribution.line.expense",
                "purchase_cost_distribution_line_expense",
                "cost_ratio",
                "expense_unit",
            ),
        ],
    )
