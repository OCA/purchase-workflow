This module provides different configuration option to manage packagings on
purchase orders.

The creation/update of purchase order line will be blocked (by constraints) if the data on the
purchase.order.line does not fit with the configuration of the product's packagings.

It's also possible to force the quantity to purchase during creation/modification of the purchase order line
if the "Force purchase quantity" is ticked on the packaging and the "Purchase only by packaging" is ticked on product.

For example, if your packaging is set to purchase by 5 units and the employee fill
the quantity with 3, the quantity will be automatically replaced by 5 (it always rounds up).
