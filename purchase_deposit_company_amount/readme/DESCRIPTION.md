This module books a foreign-currency purchase deposit at the company-currency amount
actually paid and carries that figure through to the final bill, so the deposit account
clears to zero and the exchange-rate difference lands in the inventory cost of the goods
instead of being stranded on the balance sheet.

In detail:

- Adds a Company Currency Amount field to the deposit line of a deposit
  bill, which forces the line's balance to the amount entered instead of
  converting the foreign currency amount at the exchange rate.
- Carries the company currency value of a posted deposit bill over to the
  deposit offset line of the final bill, so the deposit account closes out
  at the amount that was actually paid.
- Books the resulting exchange rate difference into the product lines, and
  reflects it in the stock valuation of the received goods.

The field is only available on the deposit line of a deposit bill raised in
a foreign currency, and the column is hidden everywhere else. Everything on
the final bill is derived from it, and a deposit nobody entered an amount
for keeps the standard rate conversion throughout.
