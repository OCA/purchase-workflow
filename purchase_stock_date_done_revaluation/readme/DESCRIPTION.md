This module revalues a **not-yet-billed incoming purchase receipt** when its
effective date (`date_done`) changes, so the inventory value reflects the
exchange rate of the new date.

It is only relevant for **purchase orders in a foreign currency** (a currency
other than the company currency): there, the receipt value in company currency
depends on the FX rate at the receipt date, so moving that date should move the
value. For company-currency purchases it has no effect.

It is meant to be used together with
[`stock_date_done`](https://github.com/OCA/stock-logistics-workflow/tree/19.0/stock_date_done),
which lets users set/edit the effective date (`date_done`) of transfers and
scraps — before validation and, permission-gated, on done records — and
propagates it to the stock moves. It does **not** depend on it, though: it
operates on the native `date_done` / `move.date` and Odoo's standard valuation,
so you can install either module on its own or both together.

Once a vendor bill is posted, the bill governs the value and this module steps
aside — no value is pinned.
