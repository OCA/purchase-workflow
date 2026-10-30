This module adds an **Import Lines** button to requests for quotation. It
opens a wizard that reads a spreadsheet (XLSX, XLS, ODS or CSV) and adds one
purchase order line per row to the current request for quotation.

The spreadsheet supports these columns:

| Column             | Required | Purchase order line field                      |
| ------------------ | -------- | ---------------------------------------------- |
| Internal Reference | Yes      | `product_id`, by the product internal reference |
| Quantity           | Yes      | `product_qty`                                  |
| Description        | No       | `name`                                         |
| Unit Price         | No       | `price_unit`                                   |
| Analytic Account   | No       | `analytic_distribution`, 100% to the account   |

An empty optional cell keeps the value Odoo computes for the line: the
default description of the product and the vendor price. The analytic account
is searched by code or by name.

All the rows are checked before any line is created: if any of them has an
error, nothing is imported and every error is reported with its row number.
