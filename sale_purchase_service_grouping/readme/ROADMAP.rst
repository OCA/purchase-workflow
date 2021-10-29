From a functional perspective, this module is similar to
`procurement_purchase_no_grouping`.

Technically, they're quite different, as service product don't generate procurements,
the resulting Purchase Order is created differently.

However, we could think about integrating the two modules so that the configuration
on the `product.category` is merged and reused. From the user perspective it would
make sense to configure this once per category for both services and stockable products.
