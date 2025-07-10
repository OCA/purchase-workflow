A note on dependencies: this module depends on stock. Mainly, for displaying qty_available of a product.
To avoid this dependency, this module could be split.

Compatibility note: purchase_order_type could be compatible as far as functionality goes, but not
for tests (adding a new required field breaks our usage of Form).
