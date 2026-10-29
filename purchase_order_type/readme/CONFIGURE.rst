To configure this module, you need to:

* Go to **Purchases > Configuration > Purchase types**
* Modify / create the purchase order types
* Enable **Default** on the order type a purchase order gets when its
  vendor has no order type. One default can be set per company, plus one
  for all companies.

To make an order type mandatory on purchase orders:

* Go to **Purchases > Configuration > Settings**
* Enable **Require Purchase Order Type**. The setting applies per company.

A purchase order then cannot be saved in the form without an order type.
New installations do not require an order type. Upgraded installations
keep requiring it for every existing company; companies created later do
not require it until the setting is enabled.
