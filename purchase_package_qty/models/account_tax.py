from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        """
        If record has price_policy and is set to 'package',
        then we need to adjust the price_unit and quantity in order to
        compute the taxes on the package price and not on the unit price.
        """
        kwargs = kwargs or dict()
        if getattr(record, "price_policy", None) == "package":
            # Case of POLine
            if hasattr(record, "product_qty_package"):
                kwargs["quantity"] = record.product_qty_package
                # kwargs["price_unit"] = record.price_unit * record.product_qty_package
        base_line = super()._prepare_base_line_for_taxes_computation(record, **kwargs)

        return base_line
