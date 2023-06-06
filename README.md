
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/purchase-workflow&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/purchase-workflow/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/purchase-workflow/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/purchase-workflow/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/purchase-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/purchase-workflow-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/purchase-workflow-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Purchase Workflow

Odoo modules for purchase and its workflow

This project aims to deal with modules related to managing purchase and their related workflow. You'll find modules that:

 - Allow to easily group purchase orders
 - Choose the cheapest supplier
 - Add validation step
 - ...


<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[procurement_purchase_no_grouping](procurement_purchase_no_grouping/) | 13.0.3.0.1 |  | Procurement Purchase No Grouping
[procurement_purchase_sale_no_grouping](procurement_purchase_sale_no_grouping/) | 13.0.1.0.0 |  | Procurement Purchase Service No Grouping
[product_form_purchase_link](product_form_purchase_link/) | 13.0.1.1.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Add an option to display the purchases lines from product
[product_supplierinfo_qty_multiplier](product_supplierinfo_qty_multiplier/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Product supplierinfo qty multiplier
[purchase_all_shipments](purchase_all_shipments/) | 13.0.1.0.0 |  | Purchase All Shipments
[purchase_allowed_product](purchase_allowed_product/) | 13.0.1.0.0 |  | This module allows to select only products that can be supplied by the vendor
[purchase_analytic_global](purchase_analytic_global/) | 13.0.1.0.0 |  | Purchase - Analytic Account Global
[purchase_blanket_order](purchase_blanket_order/) | 13.0.2.3.0 |  | Purchase Blanket Orders
[purchase_commercial_partner](purchase_commercial_partner/) | 13.0.1.0.0 |  | Add stored related field 'Commercial Supplier' on POs
[purchase_delivery_split_date](purchase_delivery_split_date/) | 13.0.1.0.5 |  | Allows Purchase Order you confirm to generate one Incoming Shipment for each expected date indicated in the Purchase Order Lines
[purchase_deposit](purchase_deposit/) | 13.0.1.0.1 |  | Option to create deposit from purchase order
[purchase_discount](purchase_discount/) | 13.0.1.1.0 |  | Purchase order lines with discounts
[purchase_exception](purchase_exception/) | 13.0.1.0.0 |  | Custom exceptions on purchase order
[purchase_force_invoiced](purchase_force_invoiced/) | 13.0.1.0.1 |  | Allows to force the billing status of the purchase order to "Invoiced"
[purchase_invoice_plan](purchase_invoice_plan/) | 13.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to purchases order, ability to manage future invoice plan
[purchase_isolated_rfq](purchase_isolated_rfq/) | 13.0.1.1.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Purchase Isolated RFQ
[purchase_landed_cost](purchase_landed_cost/) | 13.0.1.2.0 |  | Purchase cost distribution
[purchase_last_price_info](purchase_last_price_info/) | 13.0.2.0.2 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Purchase Product Last Price Info
[purchase_line_procurement_group](purchase_line_procurement_group/) | 13.0.1.0.1 |  | Group purchase order line according to procurement group
[purchase_location_by_line](purchase_location_by_line/) | 13.0.1.0.0 |  | Allows to define a specific destination location on each PO line
[purchase_manual_currency](purchase_manual_currency/) | 13.0.1.0.2 |  | Allows to manual currency of Purchase
[purchase_minimum_amount](purchase_minimum_amount/) | 13.0.1.0.1 |  | Purchase Minimum Amount
[purchase_open_qty](purchase_open_qty/) | 13.0.1.3.1 |  | Allows to identify the purchase orders that have quantities pending to invoice or to receive.
[purchase_order_approval_block](purchase_order_approval_block/) | 13.0.1.0.2 |  | Purchase Order Approval Block
[purchase_order_approved](purchase_order_approved/) | 13.0.1.1.0 |  | Add a new state 'Approved' in purchase orders.
[purchase_order_archive](purchase_order_archive/) | 13.0.1.0.0 |  | Archive Purchase Orders
[purchase_order_general_discount](purchase_order_general_discount/) | 13.0.1.0.0 |  | General discount per purchase order
[purchase_order_line_deep_sort](purchase_order_line_deep_sort/) | 13.0.1.0.0 |  | Purchase Order Line Sort
[purchase_order_line_menu](purchase_order_line_menu/) | 13.0.1.0.0 |  | Adds Purchase Order Lines Menu
[purchase_order_line_packaging_qty](purchase_order_line_packaging_qty/) | 13.0.1.0.2 |  | Define quantities according to product packaging on purchase order lines
[purchase_order_line_price_history](purchase_order_line_price_history/) | 13.0.1.0.0 |  | Purchase order line price history
[purchase_order_line_price_history_discount](purchase_order_line_price_history_discount/) | 13.0.1.0.0 |  | Purchase order line price history discount
[purchase_order_line_sequence](purchase_order_line_sequence/) | 13.0.1.0.0 |  | Adds sequence to PO lines and propagates it toInvoice lines and Stock Moves
[purchase_order_line_stock_available](purchase_order_line_stock_available/) | 13.0.1.0.0 |  | Purchase order line stock available
[purchase_order_product_recommendation](purchase_order_product_recommendation/) | 13.0.1.1.0 |  | Recommend products to buy to supplier based on history
[purchase_order_product_recommendation_brand](purchase_order_product_recommendation_brand/) | 13.0.1.0.1 |  | Allow to filter recommendations by brand
[purchase_order_product_recommendation_classification](purchase_order_product_recommendation_classification/) | 13.0.1.0.0 |  | Extends the purchase recomendator with classification filters
[purchase_order_product_recommendation_forecast](purchase_order_product_recommendation_forecast/) | 13.0.1.0.0 |  | Obtain linear progression forecast from reference years
[purchase_order_product_recommendation_secondary_unit](purchase_order_product_recommendation_secondary_unit/) | 13.0.1.0.0 |  | Add secondary unit to recommend products wizard
[purchase_order_product_recommendation_xlsx](purchase_order_product_recommendation_xlsx/) | 13.0.1.0.0 |  | Add a way to print recommended products for supplier
[purchase_order_qty_change_no_recompute](purchase_order_qty_change_no_recompute/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in purchase order line
[purchase_order_secondary_unit](purchase_order_secondary_unit/) | 13.0.2.0.0 |  | Purchase product in a secondary unit
[purchase_order_supplierinfo_update](purchase_order_supplierinfo_update/) | 13.0.1.0.2 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Update product supplierinfo with the last purchase price
[purchase_order_type](purchase_order_type/) | 13.0.1.0.1 |  | Purchase Order Type
[purchase_order_type_dashboard](purchase_order_type_dashboard/) | 13.0.1.0.0 | [![dalonsod](https://github.com/dalonsod.png?size=30px)](https://github.com/dalonsod) | Purchase Order Type Dashboard
[purchase_order_uninvoiced_amount](purchase_order_uninvoiced_amount/) | 13.0.2.2.0 |  | Purchase Order Univoiced Amount
[purchase_origin_link](purchase_origin_link/) | 13.0.1.0.0 | [![JudithAforgeFlow](https://github.com/JudithAforgeFlow.png?size=30px)](https://github.com/JudithAforgeFlow) | Add clickable link in purchase source document.
[purchase_origin_link_sale](purchase_origin_link_sale/) | 13.0.1.0.0 | [![JudithAforgeFlow](https://github.com/JudithAforgeFlow.png?size=30px)](https://github.com/JudithAforgeFlow) | Add clickable link to the Sale Order in purchase source document.
[purchase_partner_selectable_option](purchase_partner_selectable_option/) | 13.0.1.1.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Purchase Partner Selectable Option
[purchase_product_usage](purchase_product_usage/) | 13.0.1.1.1 |  | Purchase Product Usage
[purchase_propagate_qty](purchase_propagate_qty/) | 13.0.1.1.3 |  | Quantity decrease on purchase line are propagated to the corresponding stock.move
[purchase_reception_notify](purchase_reception_notify/) | 13.0.1.0.2 |  | Purchase Reception Notify
[purchase_reception_status](purchase_reception_status/) | 13.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add reception status on purchase orders
[purchase_representative](purchase_representative/) | 13.0.1.0.0 |  | Purchase Representatives will be the point of contact for RFQ's and PO's
[purchase_request](purchase_request/) | 13.0.4.3.0 |  | Use this module to have notification of requirements of materials and/or external services and keep track of such requirements.
[purchase_request_department](purchase_request_department/) | 13.0.1.0.0 |  | Purchase Request Department
[purchase_request_order_approved](purchase_request_order_approved/) | 13.0.1.0.1 |  | Purchase Request Order Approved
[purchase_request_tier_validation](purchase_request_tier_validation/) | 13.0.1.1.0 |  | Extends the functionality of Purchase Requests to support a tier validation process.
[purchase_requisition_grouped_by_procurement](purchase_requisition_grouped_by_procurement/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Purchase Requisition Grouped by Procurement
[purchase_requisition_order_remaining_qty](purchase_requisition_order_remaining_qty/) | 13.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Purchase Requisition Order Remaining Qty
[purchase_requisition_tier_validation](purchase_requisition_tier_validation/) | 13.0.1.0.0 |  | Extends the functionality of Purchase Agreements to support a tier validation process.
[purchase_security](purchase_security/) | 13.0.1.1.0 | [![joao-p-marques](https://github.com/joao-p-marques.png?size=30px)](https://github.com/joao-p-marques) | See only your purchase orders
[purchase_stock_picking_show_currency_rate](purchase_stock_picking_show_currency_rate/) | 13.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Show currency rate in purchase stock picking.
[purchase_stock_price_unit_sync](purchase_stock_price_unit_sync/) | 13.0.1.0.2 |  | Update cost price in stock moves already done
[purchase_stock_return_request](purchase_stock_return_request/) | 13.0.1.0.0 |  | Purchase Stock Return Request
[purchase_stock_secondary_unit](purchase_stock_secondary_unit/) | 13.0.1.0.2 |  | Get product quantities in a secondary unit
[purchase_stock_tier_validation](purchase_stock_tier_validation/) | 13.0.1.0.0 |  | Exclude RFQs pending to validate when procuring
[purchase_substate](purchase_substate/) | 13.0.1.0.0 |  | Purchase Sub State
[purchase_tier_validation](purchase_tier_validation/) | 13.0.1.0.0 |  | Extends the functionality of Purchase Orders to support a tier validation process.
[purchase_tier_validation_forward](purchase_tier_validation_forward/) | 13.0.1.0.1 |  | Purchase Tier Validation - Forward Option
[purchase_triple_discount](purchase_triple_discount/) | 13.0.1.0.0 |  | Manage triple discount on purchase order lines
[purchase_v12_control_menu](purchase_v12_control_menu/) | 13.0.1.0.0 |  | Purchase Control Menu from v12
[purchase_warn_message](purchase_warn_message/) | 13.0.1.0.3 |  | Add a popup warning on purchase to ensure warning is populated
[purchase_work_acceptance](purchase_work_acceptance/) | 13.0.1.1.2 |  | Purchase Work Acceptance
[supplier_calendar](supplier_calendar/) | 13.0.1.0.0 | [![NuriaMForgeFlow](https://github.com/NuriaMForgeFlow.png?size=30px)](https://github.com/NuriaMForgeFlow) | Supplier Calendar
[vendor_transport_lead_time](vendor_transport_lead_time/) | 13.0.1.2.0 |  | Purchase delay based on transport and supplier delays

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
