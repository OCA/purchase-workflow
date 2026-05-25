Avoid duplicated product codes in purchase order line descriptions.

By default, Odoo automatically prepends the Internal Reference to the product name when adding a product to a Purchase Order (e.g., "[FURN_6666] Acoustic Bloc Screens").

This module modifies that behavior by passing "display_default_code=False" to the context. 
