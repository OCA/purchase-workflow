
.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

======================
 Purchase Landed Costs
======================

This module adds the possibility to include estimated landed costs to the
average price computation. To define those landed costs, create products
for every landed costs and affect them a distribution type. Don't forget to
as well assign them a specific financial account (the one which will record
the real cost) in order to compare at the end of the year the estimation
with real accounting entries (see stock valuation). The landed costs is
defined in purchase orders. These costs will be distributed according to
the distribution type defined in landed cost:

 * value - example custom fees
 * quantity - example freight

Note : Products used to define landed cost must have a default "Distribution
Type" set (Value/Quantity).

For each landed cost position (=line) define in a PO, a draft invoice can be
pre-created at PO validation (an option need to be checked). Doing so will
allow you to see those invoices using the view invoice button directly from
the PO. You can define landed cost relative to a whole PO or by PO line (or
both) and the system will distribute them to each line according to the
chosen distribution type.

Note that the landed cost is always expressed in company currency.

Find all landed cost here : Reporting -> Purchase -> Landed costs

Stock valuation:
----------------
As the average price is also used for the stock valuation and because the
computation is based on estimation of landed cost in the PO (done at
incoming shipment reception), you will have a  difference with the actual
accounting bookings of landed cost.  Stock valuation will have to be
adjusted with a manual journal entry. In order to correct that amount, make
a sum of estimated landed cost (landed cost position) by account and
compare with the real account chart value. You can access those
informations through this menu: Reporting -> Purchase -> Landed costs

Warning:
--------

 * Average price will be computed based on the estimation made on the PO - not
   from real cost. This is due to the way OpenERP compute average stock: it
   stores the updated value at every input, no history, so no way to redefine
   the value afterwards.

   i.e.
    - incomming 01: 100 product A at 50.- AVG = 50.-, stock = 100
    - incomming 02: 100 product A at 60.- AVG = 55.-, stock = 200
    - delivery 01: 50 product A AVG = 55.-, stock = 150
    - Receive the real landed cost of 10.- for incomming 01
  => cannot compute back because no historical price was store for every
  transaction. Moreover, in OpenERP I can even
  set another average price for a product using the update wizard.


 * As the price type of OpenERP is not really well handled, we need to be sure
   that price type of cost price in product form is the same as the company
   one. Otherwise, when computing the AVG price, it make the convertion in
   company currency from the price type currency. This is not related to this
   module, but from the core of OpenERP. If you use this module in
   multi-company and different currency between company, you'll have to not
   share the product between them, even if product are the same (bug:
   https://bugs.launchpad.net/ocb-addons/+bug/1238525).

TODO/Ideas:
-----------
 * Manage multi-currencies landed costs in PO
 * Have the shipped date in landed cost instead of PO date for a better
   analysis
 * Compute a average purchase price per products while keep cost price as it is
   now


Credits
=======

Contributors
------------

  * Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>
  * Ferdinand Gasauer <ferdinand.gasauer@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
