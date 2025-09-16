This module provides compatibility between the OCA purchase_reception_status
module and Odoo's native purchase_stock module.

When both modules are installed, this glue module automatically:

* Overrides Odoo's native receipt_status computation to use the OCA logic
* Hides redundant native receipt_status displays in views
* Ensures the preferred OCA logic is applied instead of Odoo's approach

