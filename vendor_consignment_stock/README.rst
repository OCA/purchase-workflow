Vendor Consignment Stock
========================

This module allows to have stock in the company warehouse that still belongs to
a vendor. This practice is normally known as "Vendor Consignment Stock".

This module implements a special flow that starts with a Sale Order. Three
cases are possible depending on the owner specified in the sale order line.

1. If no owner is specified in the sale order line, it means we are selling our
   own goods. As usual in standard Odoo, the procurement will choose routes as
   configured in the product, category, warehouse or order line. Only stock
   belonging to us will be reserved in the generated delivery.

2. If the owner specified in the sale order line is the customer of the order,
   that means that we are asked to send to a customer their own stock. We can
   do so right away, and only his stock will be reserved in the generated
   delivery.

3. If the owner specified in the sale order line is not he customer of the
   order, that means that we are dealing with "Vendor Consignment Stock". Even
   though the goods are already in our warehouse, we need to purchase them from
   the vendor. In that case, on validation of the sale, a special Request for
   Quotation will be generated, with the following characteristics:

   - It is marked as "VCI", and can be easily found with a "VCI" filter that
     has been added to the search view.
   - The supplier is not the one configured in the product as in the case for
     normal purchases. It is instead the owner that has been specified in the
     sale line.
   - Once validated, this purchase will not generate a picking since we already
     have the goods in stock. Instead, validation of the purchase will make the
     delivery to the customer available.

Note that the VCI flow (3) is of the "Make to order" kind. That means that the
purchase order will always be for the quantity sold, even if a small quantity
would suffice. That logic is very similar to the standard "Make to Order, Buy"
flow in Odoo.

Also note that the user has to choose manually the vendor in the sale order line in
order to use the special VCI flow (3. above). On the other hand, the routes
"Make to Order" and "Buy VCI" are automatically selected in the generated
procurement.

In the same fashion of the purchase and mrp modules, the routes and procurement
rules are generated and updated automatically for all warehouses. A flag
labeled "Purchase from VCI to resupply this warehouse" has been added to choose
if we want this to happen.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20vendor_consignment_stock%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.
