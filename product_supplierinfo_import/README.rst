.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Product supplierinfo import
===========================
This module allows to load product.supplierinfo list from a file.

Known issues / Roadmap
======================
| The file format should have these colummns:
| keys = ['Supplier', **'ProductCode'**, 'Sequence', 'ProductSupplierCode', 'ProductSupplierName', 'Delay', 'MinQty', **'Price'**]
| *Bold keys are required columns.*
| *'Supplier'* Key could be supplier code or name.

Credits
=======

Contributors
------------
* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
