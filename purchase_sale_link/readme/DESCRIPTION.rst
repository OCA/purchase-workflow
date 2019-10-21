Adds a button on Purchase Orders created automatically from Sale Orders, to navigate easily from the Purchase Order to the related Sale Orders.
Adds also a button on these Sale Orders to navigate to the related Purchase Orders.

This module works with Purchase Orders created automatically from Sale Orders with storable as well as service products.
It overwrites some methods from the core module `sale_purchase <https://github.com/odoo/odoo/tree/12.0/addons/sale_purchase>`_ that were `disabled on November 2018 <https://github.com/odoo/odoo/commit/2aa87253d14f5960ff04ed358d42354111ff7ead>`_ because they were linking the Purchase Orders created from Sale Orders with service products only.
