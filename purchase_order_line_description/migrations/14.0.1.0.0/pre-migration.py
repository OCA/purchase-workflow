import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)
_field_renames = [
    (
        "res_config_settings",
        "res_config_settings",
        "group_use_product_description_per_po_line",
        "config_product_in_purchase_order_lines",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.debug("Running migrate script for XXX module")

    openupgrade.rename_fields(env, _field_renames)
