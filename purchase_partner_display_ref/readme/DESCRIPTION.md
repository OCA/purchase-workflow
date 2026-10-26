This module prefixes the supplier reference (`res.partner.supplier_ref`) to the
vendor's `display_name` whenever it is rendered inside a Purchase view —
shown as `[V00045] Acme Supplies` in the vendor field of a purchase order, both
in the dropdown and on the selected value.

The decoration mechanism lives in the generic `partner_display_ref` module; this
module injects the `partner_display_ref_field` context key (set to
`supplier_ref`) into the Purchase views and registers `supplier_ref` as a
dependency of the vendor `display_name`. Other views that read `display_name`
continue to see the plain partner name.
