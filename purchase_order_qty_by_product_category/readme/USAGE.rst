Once the module is installed, you can configure whether quantities should be split by UoM by default.
To do so, you can:

1. configure an ``ir.config_parameter`` record, with key "purchase_ordered_qty_by_product_category.split_by_uom" and value "1"

2. go to the Purchase settings and flag the "Split Quantity Category By UoM" checkbox

You can also configure whether reference UoM should be used for grouping. To do so, you can:

1. configure an ``ir.config_parameter`` record, with key "purchase_ordered_qty_by_product_category.split_by_uom_reference" and value "1"

2. go to the Purchase settings and flag the "Split Quantity Category By Reference UoM" checkbox

NB: splitting by reference UoM is available only if splitting by UoM is activated first.
