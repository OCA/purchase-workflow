[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/142/14.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-purchase-workflow-142)
[![Build Status](https://travis-ci.com/OCA/purchase-workflow.svg?branch=14.0)](https://travis-ci.com/OCA/purchase-workflow)
[![codecov](https://codecov.io/gh/OCA/purchase-workflow/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/purchase-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/purchase-workflow-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/purchase-workflow-14-0/?utm_source=widget)

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
[procurement_batch_generator](procurement_batch_generator/) | 14.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Wizard to replenish from product tree view
[product_form_purchase_link](product_form_purchase_link/) | 14.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Add an option to display the purchases lines from product
[purchase_advance_payment](purchase_advance_payment/) | 14.0.1.0.0 |  | Allow to add advance payments on purchase orders
[purchase_cancel_reason](purchase_cancel_reason/) | 14.0.1.0.0 |  | Purchase Cancel Reason
[purchase_commercial_partner](purchase_commercial_partner/) | 14.0.1.0.0 |  | Add stored related field 'Commercial Supplier' on POs
[purchase_delivery_split_date](purchase_delivery_split_date/) | 14.0.1.1.1 |  | Allows Purchase Order you confirm to generate one Incoming Shipment for each expected date indicated in the Purchase Order Lines
[purchase_deposit](purchase_deposit/) | 14.0.1.1.0 |  | Option to create deposit from purchase order
[purchase_discount](purchase_discount/) | 14.0.1.1.1 |  | Purchase order lines with discounts
[purchase_exception](purchase_exception/) | 14.0.1.0.0 |  | Custom exceptions on purchase order
[purchase_fop_shipping](purchase_fop_shipping/) | 14.0.1.1.0 |  | Purchase Free-Of-Payment shipping
[purchase_force_invoiced](purchase_force_invoiced/) | 14.0.1.0.0 |  | Allows to force the billing status of the purchase order to "Invoiced"
[purchase_invoice_plan](purchase_invoice_plan/) | 14.0.1.1.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to purchases order, ability to manage future invoice plan
[purchase_isolated_rfq](purchase_isolated_rfq/) | 14.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Purchase Isolated RFQ
[purchase_last_price_info](purchase_last_price_info/) | 14.0.2.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Purchase Product Last Price Info
[purchase_location_by_line](purchase_location_by_line/) | 14.0.1.0.1 |  | Allows to define a specific destination location on each PO line
[purchase_manual_currency](purchase_manual_currency/) | 14.0.1.0.0 |  | Allows to manual currency of Purchase
[purchase_minimum_amount](purchase_minimum_amount/) | 14.0.1.0.1 |  | Purchase Minimum Amount
[purchase_open_qty](purchase_open_qty/) | 14.0.1.0.1 |  | Allows to identify the purchase orders that have quantities pending to invoice or to receive.
[purchase_order_approval_block](purchase_order_approval_block/) | 14.0.1.0.2 |  | Purchase Order Approval Block
[purchase_order_approved](purchase_order_approved/) | 14.0.1.1.0 |  | Add a new state 'Approved' in purchase orders.
[purchase_order_archive](purchase_order_archive/) | 14.0.1.0.0 |  | Archive Purchase Orders
[purchase_order_line_deep_sort](purchase_order_line_deep_sort/) | 14.0.1.0.0 |  | Purchase Order Line Sort
[purchase_order_line_description_picking](purchase_order_line_description_picking/) | 14.0.1.0.0 |  | Purchase Order Line Name To Picking
[purchase_order_line_menu](purchase_order_line_menu/) | 14.0.1.0.0 |  | Adds Purchase Order Lines Menu
[purchase_order_line_packaging_qty](purchase_order_line_packaging_qty/) | 14.0.1.0.0 |  | Define quantities according to product packaging on purchase order lines
[purchase_order_line_price_history](purchase_order_line_price_history/) | 14.0.1.0.0 |  | Purchase order line price history
[purchase_order_line_sequence](purchase_order_line_sequence/) | 14.0.1.0.0 |  | Adds sequence to PO lines and propagates it toInvoice lines and Stock Moves
[purchase_order_secondary_unit](purchase_order_secondary_unit/) | 14.0.1.0.0 |  | Purchase product in a secondary unit
[purchase_order_type](purchase_order_type/) | 14.0.1.0.2 |  | Purchase Order Type
[purchase_order_uninvoiced_amount](purchase_order_uninvoiced_amount/) | 14.0.1.1.0 |  | Show uninvoiced amount on purchase order tree.
[purchase_partner_incoterm](purchase_partner_incoterm/) | 14.0.1.0.0 |  | Add a an incoterm field for supplier and use it on purchase order
[purchase_product_usage](purchase_product_usage/) | 14.0.1.1.0 |  | Purchase Product Usage
[purchase_propagate_qty](purchase_propagate_qty/) | 14.0.1.0.1 |  | Quantity decrease on purchase line are propagated to the corresponding stock.move
[purchase_quick](purchase_quick/) | 14.0.1.0.1 |  | Quick Purchase order
[purchase_reception_notify](purchase_reception_notify/) | 14.0.1.0.0 |  | Purchase Reception Notify
[purchase_reception_status](purchase_reception_status/) | 14.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add reception status on purchase orders
[purchase_report_menu_move](purchase_report_menu_move/) | 14.0.1.0.0 | [![newtratip](https://github.com/newtratip.png?size=30px)](https://github.com/newtratip) | Purchase Report Menu Move
[purchase_request](purchase_request/) | 14.0.1.3.2 |  | Use this module to have notification of requirements of materials and/or external services and keep track of such requirements.
[purchase_request_cancel_confirm](purchase_request_cancel_confirm/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Purchase Request Cancel Confirm
[purchase_request_department](purchase_request_department/) | 14.0.1.0.0 |  | Purchase Request Department
[purchase_request_exception](purchase_request_exception/) | 14.0.1.0.0 |  | Custom exceptions on purchase request
[purchase_request_tier_validation](purchase_request_tier_validation/) | 14.0.2.1.0 |  | Extends the functionality of Purchase Requests to support a tier validation process.
[purchase_request_type](purchase_request_type/) | 14.0.1.0.1 |  | Purchase Request Type
[purchase_requisition_tier_validation](purchase_requisition_tier_validation/) | 14.0.1.0.0 |  | Extends the functionality of Purchase Agreements to support a tier validation process.
[purchase_rfq_number](purchase_rfq_number/) | 14.0.1.0.0 |  | Different sequence for purchase for quotations
[purchase_security](purchase_security/) | 14.0.1.0.0 | [![joao-p-marques](https://github.com/joao-p-marques.png?size=30px)](https://github.com/joao-p-marques) | See only your purchase orders
[purchase_tier_validation](purchase_tier_validation/) | 14.0.2.0.1 |  | Extends the functionality of Purchase Orders to support a tier validation process.
[purchase_work_acceptance](purchase_work_acceptance/) | 14.0.1.1.1 |  | Purchase Work Acceptance
[purchase_work_acceptance_evaluation](purchase_work_acceptance_evaluation/) | 14.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Purchase Work Acceptance Evaluation
[purchase_work_acceptance_invoice_plan](purchase_work_acceptance_invoice_plan/) | 14.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Purchase Work Acceptance Invoice Plan
[purchase_work_acceptance_late_fines](purchase_work_acceptance_late_fines/) | 14.0.1.0.0 | [![Saran440](https://github.com/Saran440.png?size=30px)](https://github.com/Saran440) | Purchase Work Acceptance - Late Delivery Fines
[vendor_transport_lead_time](vendor_transport_lead_time/) | 14.0.1.0.0 |  | Purchase delay based on transport and supplier delays

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
