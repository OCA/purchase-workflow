This module allows a user to indicate that a service is subcontracted.
It provides the ability to create purchases from procurement processes.

This is a base module, by itself it does not provide any function to the end user.
Upon installation of specific modules for sale / manufacturing, some new behaviors
can be achieved, examples:

* Add a service to a kit Bill of Materials, use the kit in a sales order. On
  confirmation, an additional PO for the service is going to be created.
* Add subcontracted services to BOMs. When a manufacturing order is created a
  PO is triggered for the service to be subcontracted.
* Add subcontracted services to sales order. When the SO is confirmed, it
  creates a PO for the service.
