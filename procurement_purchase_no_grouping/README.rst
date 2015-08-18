No grouping on procurement purchases
====================================

This module allows to not group generated purchase orders from procurements.
The grouping behaviour can be configurable at product category level.

Configuration
=============

Go to each product category, and select one of these values in the field
"Procured purchase grouping":

* *Standard grouping (default)*: With this option, procurements will generate
  purchase orders as always, grouping lines and orders when possible.
* *No line grouping*: With this value, if there are any open purchase order
  for the same supplier, it will be reused, but lines won't be merged.
* *No order grouping*: This option will prevent any kind of grouping.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
