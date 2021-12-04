from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.drop_columns(
        env.cr,
        [
            ("product_product", "last_supplier_id"),
            ("product_template", "last_supplier_id"),
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "purchase_last_price_info.product_product_last_purchase_info_form_view",
            "purchase_last_price_info.product_template_last_purchase_info_form_view",
        ],
    )
