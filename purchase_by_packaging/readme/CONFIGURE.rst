Following options are available to define which packaging type can be purchased and
which product can only be purchased by packaging.

* Can be purchased: On product packaging type model, this checkbox defines if product
  packagings from this particular type are available to be selected on purchase
  order line.

* Purchase only by packaging: On product template model, this checkbox restricts
  purchases of these products if no packaging is selected on the purchase order line.
  If no packaging is selected, it will either be auto-assigned if the quantity
  on the purchase order line matches a packaging quantity or an error will be raised.

* Force purchase quantity (on the packaging): force rounds up the quantity during
  creation/modification of the purchase order line with the factor set on the packaging.
