For configuration of displaying secondary unit information in purchase reports and
the Purchase Order portal, see the guidelines provided in product_secondary_unit.

## Settings Visibility

When installing this module, all internal users are automatically added to the
`product_secondary_unit.group_purchase_secondary_unit` security group. This makes
the Purchase-related "Hide Secondary Qty Column" and "Secondary Unit Price Display"
settings visible in **Settings > Units of Measure**.

If you installed this module before these report presentation settings were introduced
in `product_secondary_unit`, users may not see these configuration options. To fix this:

1. Go to **Settings > Users & Companies > Groups**
2. Search for "Purchase Secondary Unit"
3. Add the relevant users to that group
