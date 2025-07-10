# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


def migrate_order_discount_to_discount1(env):
    openupgrade.add_fields(
        env,
        [
            (
                "discount1",
                "purchase.order.line",
                "purchase_order_line",
                "float",
                "numeric",
                "purchase_triple_discount",
                0.0,
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line
        SET discount1 = discount;
        """,
    )


def migrate_supplierinfo_discount_to_discount1(env):
    openupgrade.add_fields(
        env,
        [
            (
                "discount1",
                "product.supplierinfo",
                "product_supplierinfo",
                "float",
                "numeric",
                "purchase_triple_discount",
                0.0,
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_supplierinfo
        SET discount1 = discount;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    migrate_order_discount_to_discount1(env)
    migrate_supplierinfo_discount_to_discount1(env)
