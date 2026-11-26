Denormalizes `product.active` onto `product.supplierinfo` so the *Active
Products* search filter runs on a single indexed boolean column instead
of two JOINs with an OR condition.

This addresses the upstream performance issue reported since Odoo 16.0
([odoo/odoo#106058](https://github.com/odoo/odoo/issues/106058)): on
databases with millions of products, the standard *Active Products*
filter causes queries lasting more than 10 minutes.

The standard *Active Products* filter uses the domain:

    ['|', ('product_tmpl_id.active', '=', True), ('product_id.active', '=', True)]

This forces two JOINs and an OR on large tables. On millions of rows
Postgres cannot push this down to an index on `product_supplierinfo` (no
local active column) and falls back to a full-table scan.

This module adds `is_product_active`, a stored and indexed boolean on
`product.supplierinfo` that mirrors the active state of the linked
product or template. The filter domain is replaced by the single-column
lookup:

    [('is_product_active', '=', True)]
