No configuration required. Install the module and the *Active Products*
filter in **Purchase → Configuration → Vendor Pricelists** will
automatically use the indexed column.

The field `is_product_active` is kept in sync automatically:

- When a `product.template` is archived or unarchived, all its
  supplierinfo rows (direct and variant-linked) are updated.
- When a `product.product` variant is archived or unarchived, its
  variant-linked supplierinfo rows are updated.

A `post_init_hook` backfills existing rows on first install using direct
SQL.
