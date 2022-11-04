
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/purchase-workflow&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/purchase-workflow/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/purchase-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/purchase-workflow-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/purchase-workflow-15-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# purchase-workflow

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[procurement_purchase_no_grouping](procurement_purchase_no_grouping/) | 15.0.1.0.1 |  | Procurement Purchase No Grouping
[product_form_purchase_link](product_form_purchase_link/) | 15.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Add an option to display the purchases lines from product
[purchase_advance_payment](purchase_advance_payment/) | 15.0.1.0.0 |  | Allow to add advance payments on purchase orders
[purchase_analytic_global](purchase_analytic_global/) | 15.0.1.0.1 |  | Purchase - Analytic Account Global
[purchase_blanket_order](purchase_blanket_order/) | 15.0.1.3.0 |  | Purchase Blanket Orders
[purchase_default_terms_conditions](purchase_default_terms_conditions/) | 15.0.1.0.1 |  | This module allows purchase default terms & conditions
[purchase_delivery_split_date](purchase_delivery_split_date/) | 15.0.1.0.0 |  | Allows Purchase Order you confirm to generate one Incoming Shipment for each expected date indicated in the Purchase Order Lines
[purchase_deposit](purchase_deposit/) | 15.0.1.0.0 |  | Option to create deposit from purchase order
[purchase_discount](purchase_discount/) | 15.0.1.0.2 |  | Purchase order lines with discounts
[purchase_exception](purchase_exception/) | 15.0.1.0.0 |  | Custom exceptions on purchase order
[purchase_force_invoiced](purchase_force_invoiced/) | 15.0.1.0.0 |  | Allows to force the billing status of the purchase order to "Invoiced"
[purchase_location_by_line](purchase_location_by_line/) | 15.0.1.0.0 |  | Allows to define a specific destination location on each PO line
[purchase_open_qty](purchase_open_qty/) | 15.0.1.0.0 |  | Allows to identify the purchase orders that have quantities pending to invoice or to receive.
[purchase_order_line_menu](purchase_order_line_menu/) | 15.0.1.0.0 |  | Adds Purchase Order Lines Menu
[purchase_order_line_price_history](purchase_order_line_price_history/) | 15.0.1.0.0 |  | Purchase order line price history
[purchase_order_line_stock_available](purchase_order_line_stock_available/) | 15.0.1.0.0 |  | Purchase order line stock available
[purchase_order_no_zero_price](purchase_order_no_zero_price/) | 15.0.1.0.0 |  | Prevent zero price lines on Purchase Orders
[purchase_order_product_recommendation](purchase_order_product_recommendation/) | 15.0.1.0.1 |  | Recommend products to buy to supplier based on history
[purchase_order_qty_change_no_recompute](purchase_order_qty_change_no_recompute/) | 15.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in purchase order line
[purchase_order_supplierinfo_update](purchase_order_supplierinfo_update/) | 15.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Update product supplierinfo with the last purchase price
[purchase_order_type](purchase_order_type/) | 15.0.1.0.0 |  | Purchase Order Type
[purchase_partner_incoterm](purchase_partner_incoterm/) | 15.0.3.0.0 | [![TDu](https://github.com/TDu.png?size=30px)](https://github.com/TDu) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Add a an incoterm field for supplier and use it on purchase order
[purchase_partner_selectable_option](purchase_partner_selectable_option/) | 15.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Purchase Partner Selectable Option
[purchase_receipt_expectation](purchase_receipt_expectation/) | 15.0.1.0.0 |  | Purchase Receipt Expectation
[purchase_receipt_expectation_manual](purchase_receipt_expectation_manual/) | 15.0.1.0.0 |  | Purchase Receipt Expectation - Manual
[purchase_receipt_expectation_manual_split](purchase_receipt_expectation_manual_split/) | 15.0.2.0.0 |  | Purchase Receipt Expectation - Manual w/ Split
[purchase_reception_notify](purchase_reception_notify/) | 15.0.1.0.0 |  | Purchase Reception Notify
[purchase_request](purchase_request/) | 15.0.1.1.0 |  | Use this module to have notification of requirements of materials and/or external services and keep track of such requirements.
[purchase_request_department](purchase_request_department/) | 15.0.1.0.0 |  | Purchase Request Department
[purchase_request_tier_validation](purchase_request_tier_validation/) | 15.0.1.0.0 |  | Extends the functionality of Purchase Requests to support a tier validation process.
[purchase_requisition_tier_validation](purchase_requisition_tier_validation/) | 15.0.1.0.0 |  | Extends the functionality of Purchase Agreements to support a tier validation process.
[purchase_tier_validation](purchase_tier_validation/) | 15.0.1.0.0 |  | Extends the functionality of Purchase Orders to support a tier validation process.
[purchase_triple_discount](purchase_triple_discount/) | 15.0.1.0.0 |  | Manage triple discount on purchase order lines

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
