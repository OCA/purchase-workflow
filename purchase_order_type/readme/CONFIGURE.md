To configure this module, you need to:

- Go to **Purchases \> Configuration \> Purchase types**
- Modify / create the purchase order types
- Enable **Default** on the order type a purchase order gets when its
  vendor has no order type. One default can be set per company, plus one
  for all companies.

To make an order type mandatory on purchase orders:

- Go to **Purchases \> Configuration \> Settings**
- Enable **Require Purchase Order Type**. The setting applies per company.

A purchase order then cannot be saved in the form without an order type.
New installations leave this setting disabled. When upgrading from the
1.x series of this module, the migration enables it for existing
companies and preserves the legacy defaults. Upgrades from 19.0.2.0.0
retain the configured defaults and company settings.
