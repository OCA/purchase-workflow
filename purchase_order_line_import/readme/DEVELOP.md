The wizard `purchase.order.line.import` is built to be extended. Each row of the
file reaches the hooks as a dictionary that maps the column keys to the cell
values, already stripped, and only holds the columns present in the file. A hook
that raises a `UserError` reports its message as the error of that row, and
the import goes on checking the next rows.

- `_get_import_columns()`: the columns the file accepts. Each one is a
  dictionary with `key`, `label`, `help` and `required`.
- `_prepare_order_line_vals(row)`: the values of the purchase order line created
  for a row.
- `_create_order_lines(vals_list)`: creates the lines of all the rows once every
  row is valid, after the existing lines of the order.
- `_get_product_domain(row)` and `_get_product(row)`: the search of the product
  of a row.
- `_get_product_qty(row)`: the quantity of a row.
- `_get_analytic_account_domain(row)` and `_get_analytic_distribution(row)`: the
  search of the analytic account of a row, and the analytic distribution it
  gives.
- `_parse_float(value, label)`: converts a cell to a number, with the separators
  inferred by `base_import`.

A new column is added by extending `_get_import_columns()`, and its value is
used in `_prepare_order_line_vals()`. It is then part of the downloaded
template and recognized in the uploaded files, by its label or by its key:

```python
from odoo import _, models


class PurchaseOrderLineImport(models.TransientModel):
    _inherit = "purchase.order.line.import"

    def _get_import_columns(self):
        columns = super()._get_import_columns()
        columns.append(
            {
                "key": "discount",
                "label": _("Discount"),
                "help": _("Discount in %."),
                "required": False,
            }
        )
        return columns

    def _prepare_order_line_vals(self, row):
        vals = super()._prepare_order_line_vals(row)
        if row.get("discount"):
            vals["discount"] = self._parse_float(row["discount"], _("Discount"))
        return vals
```

The search of an existing column is changed through its domain method, for
instance to accept only the products the vendor of the order sells:

```python
    def _get_product_domain(self, row):
        domain = super()._get_product_domain(row)
        partner = self.order_id.partner_id.commercial_partner_id
        return domain + [("seller_ids.partner_id", "=", partner.id)]
```
