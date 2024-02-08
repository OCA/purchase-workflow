
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/purchase-workflow&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/purchase-workflow/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/purchase-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/purchase-workflow-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/purchase-workflow-16-0/?utm_source=widget)

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
[product_supplier_code_purchase](product_supplier_code_purchase/) | 16.0.1.0.0 |  | This module adds to the purchase order line the supplier code defined in the product.
[product_supplierinfo_qty_multiplier](product_supplierinfo_qty_multiplier/) | 16.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Product supplierinfo qty multiplier
[purchase_advance_payment](purchase_advance_payment/) | 16.0.1.0.0 |  | Allow to add advance payments on purchase orders
[purchase_all_shipments](purchase_all_shipments/) | 16.0.1.0.0 |  | Purchase All Shipments
[purchase_allowed_product](purchase_allowed_product/) | 16.0.2.1.0 |  | This module allows to select only products that can be supplied by the vendor
[purchase_blanket_order](purchase_blanket_order/) | 16.0.2.0.1 |  | Purchase Blanket Orders
[purchase_commercial_partner](purchase_commercial_partner/) | 16.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add stored related field 'Commercial Supplier' on POs
[purchase_default_terms_conditions](purchase_default_terms_conditions/) | 16.0.1.0.2 |  | This module allows purchase default terms & conditions
[purchase_delivery_split_date](purchase_delivery_split_date/) | 16.0.1.0.1 |  | Allows Purchase Order you confirm to generate one Incoming Shipment for each expected date indicated in the Purchase Order Lines
[purchase_deposit](purchase_deposit/) | 16.0.1.0.1 |  | Option to create deposit from purchase order
[purchase_discount](purchase_discount/) | 16.0.1.2.0 |  | Purchase order lines with discounts
[purchase_exception](purchase_exception/) | 16.0.1.0.0 |  | Custom exceptions on purchase order
[purchase_fop_shipping](purchase_fop_shipping/) | 16.0.1.0.0 |  | Purchase Free-Of-Payment shipping
[purchase_force_invoiced](purchase_force_invoiced/) | 16.0.1.0.1 |  | Allows to force the billing status of the purchase order to "Invoiced"
[purchase_invoice_method](purchase_invoice_method/) | 16.0.1.0.0 |  | Allow to force the invoice method of a purchase
[purchase_invoice_plan](purchase_invoice_plan/) | 16.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to purchases order, ability to manage future invoice plan
[purchase_last_price_info](purchase_last_price_info/) | 16.0.1.0.1 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Purchase Product Last Price Info
[purchase_line_procurement_group](purchase_line_procurement_group/) | 16.0.1.0.0 |  | Group purchase order line according to procurement group
[purchase_location_by_line](purchase_location_by_line/) | 16.0.1.0.0 |  | Allows to define a specific destination location on each PO line
[purchase_lot](purchase_lot/) | 16.0.1.0.0 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Purchase Lot
[purchase_manual_delivery](purchase_manual_delivery/) | 16.0.1.1.0 |  | Prevents pickings to be auto generated upon Purchase Order confirmation and adds the ability to manually generate them as the supplier confirms the different purchase order lines.
[purchase_merge](purchase_merge/) | 16.0.1.0.1 |  | Wizard to merge purchase with required conditions
[purchase_no_rfq](purchase_no_rfq/) | 16.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Purchase Order - No Request For Quotation
[purchase_only_by_packaging](purchase_only_by_packaging/) | 16.0.1.0.0 |  | Manage purchase of packaging
[purchase_open_qty](purchase_open_qty/) | 16.0.2.0.1 |  | Allows to identify the purchase orders that have quantities pending to invoice or to receive.
[purchase_order_approved](purchase_order_approved/) | 16.0.1.0.0 |  | Add a new state 'Approved' in purchase orders.
[purchase_order_archive](purchase_order_archive/) | 16.0.1.0.0 |  | Archive Purchase Orders
[purchase_order_general_discount](purchase_order_general_discount/) | 16.0.1.0.0 |  | General discount per purchase order
[purchase_order_hide_receipt_status](purchase_order_hide_receipt_status/) | 16.0.1.0.1 |  | Purchase Order Hide Receipt Status
[purchase_order_line_menu](purchase_order_line_menu/) | 16.0.2.1.0 |  | Adds Purchase Order Lines Menu
[purchase_order_no_zero_price](purchase_order_no_zero_price/) | 16.0.1.0.1 |  | Prevent zero price lines on Purchase Orders
[purchase_order_owner](purchase_order_owner/) | 16.0.1.0.0 |  | Purchase Order Owner
[purchase_order_product_recommendation](purchase_order_product_recommendation/) | 16.0.1.1.0 |  | Recommend products to buy to supplier based on history
[purchase_order_purchase_manager](purchase_order_purchase_manager/) | 16.0.1.0.1 | [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) | Purchase Manager from Supplier in Purchase Order
[purchase_order_supplierinfo_update](purchase_order_supplierinfo_update/) | 16.0.1.0.1 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Update product supplierinfo with the last purchase price
[purchase_order_type](purchase_order_type/) | 16.0.1.0.1 |  | Purchase Order Type
[purchase_order_type_dashboard](purchase_order_type_dashboard/) | 16.0.1.0.0 | [![dalonsod](https://github.com/dalonsod.png?size=30px)](https://github.com/dalonsod) | Purchase Order Type Dashboard
[purchase_order_uninvoiced_amount](purchase_order_uninvoiced_amount/) | 16.0.1.0.1 |  | Purchase Order Univoiced Amount
[purchase_order_weight_volume](purchase_order_weight_volume/) | 16.0.2.2.0 | [![ilyasProgrammer](https://github.com/ilyasProgrammer.png?size=30px)](https://github.com/ilyasProgrammer) | Display purchase order weight and volume
[purchase_packaging_level_qty](purchase_packaging_level_qty/) | 16.0.1.0.0 |  | Display purchase order packaging level quantity
[purchase_partner_incoterm](purchase_partner_incoterm/) | 16.0.1.0.0 | [![TDu](https://github.com/TDu.png?size=30px)](https://github.com/TDu) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Add a an incoterm field for supplier and use it on purchase order
[purchase_partner_selectable_option](purchase_partner_selectable_option/) | 16.0.1.0.3 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Purchase Partner Selectable Option
[purchase_product_packaging_container_deposit](purchase_product_packaging_container_deposit/) | 16.0.1.0.0 |  | Purchase Product Packaging Container Deposit
[purchase_reception_status](purchase_reception_status/) | 16.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add reception status on purchase orders
[purchase_request](purchase_request/) | 16.0.1.0.3 |  | Use this module to have notification of requirements of materials and/or external services and keep track of such requirements.
[purchase_request_tier_validation](purchase_request_tier_validation/) | 16.0.1.0.0 |  | Extends the functionality of Purchase Requests to support a tier validation process.
[purchase_requisition_tier_validation](purchase_requisition_tier_validation/) | 16.0.1.0.0 |  | Extends the functionality of Purchase Agreements to support a tier validation process.
[purchase_security](purchase_security/) | 16.0.1.0.0 | [![pilarvargas-tecnativa](https://github.com/pilarvargas-tecnativa.png?size=30px)](https://github.com/pilarvargas-tecnativa) | See only your purchase orders
[purchase_stock_packaging](purchase_stock_packaging/) | 16.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allows to transmit the product packaging from the procurement values to the generated purchase order line
[purchase_tag](purchase_tag/) | 16.0.1.1.0 |  | Allows to add multiple tags to purchase orders
[purchase_tier_validation](purchase_tier_validation/) | 16.0.1.1.0 |  | Extends the functionality of Purchase Orders to support a tier validation process.
[purchase_triple_discount](purchase_triple_discount/) | 16.0.1.0.0 |  | Manage triple discount on purchase order lines
[purchase_warn_message](purchase_warn_message/) | 16.0.1.0.0 |  | Add a popup warning on purchase to ensure warning is populated
[sale_purchase_force_vendor](sale_purchase_force_vendor/) | 16.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Purchase Force Vendor
[supplier_calendar](supplier_calendar/) | 16.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Supplier Calendar

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
