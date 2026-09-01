Register the deposit with the standard *Register Deposit* wizard, and enter
the company currency amount actually paid in the Company Currency Amount
column of the deposit bill before posting it. The column is optional, and
can be shown from the bill line list.

Create the final bill from the purchase order as usual. The deposit offset
line is pinned to the amount entered on the deposit bill, and the exchange
rate difference is added to the product lines.

The example below follows a purchase order of USD 100 with a 30% deposit,
where the deposit of USD 30 is settled for JPY 3900, the rate on the deposit
bill date is USD 1 = JPY 150, and the rate on the final bill date is
USD 1 = JPY 160.

**Deposit bill.** Without the module the deposit is converted at the rate of
the day; with it, the balance is forced to the amount that was really paid.

| Without this module | | | With this module | | |
| --- | ---: | ---: | --- | ---: | ---: |
| Deposit (asset) | $30 | 4500 | Deposit (asset) | $30 | 3900 |
| Payable | -$30 | -4500 | Payable | -$30 | -3900 |

**Final bill.** The offset line is read back from the posted deposit bill, so
the deposit account closes out at what was paid and the difference lands in
the goods instead.

| Without this module | | | With this module | | |
| --- | ---: | ---: | --- | ---: | ---: |
| Product | $100 | 16000 | Product | $100 | 15100 |
| Deposit (asset) | -$30 | -4800 | Deposit (asset) | -$30 | -3900 |
| Payable | -$70 | -11200 | Payable | -$70 | -11200 |

Without the module the deposit account is left with JPY 300 that no further
document will clear, and the goods are valued at the closing rate alone. With
the module the deposit account is back to zero, and the product line carries
the 3900 paid for the deposit plus USD 70 at the current rate; the payable is
the remaining USD 70 at that rate in both cases.

The column only appears on a deposit bill in a foreign currency, the deposit
being the one amount known outside Odoo. In the company currency there is no
conversion to override, so the field is refused there.

Everything on the final bill is derived from what was entered: the offset
line is read back from the posted deposit bill and the goods lines take the
rate difference. Leaving the field empty on the deposit bill opts out of all
of it -- the deposit, the offset and the goods are then converted at the
exchange rate exactly as Odoo does without this module.
