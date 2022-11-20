from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_field_data(self, field_name):
        """Returns the contents of a field by name

        Args:
            field_name (str): The name of the field in the model

        Returns:
            str: content field
        """
        field_content = self[field_name]
        data = self.fields_get([field_name])
        field_type = data[field_name]["type"]
        if field_type == "many2one":
            return field_content.display_name
        elif field_type in ["one2many", "many2many"]:
            return ",".join(list(map(lambda rec: rec.name, field_content)))
        return field_content
