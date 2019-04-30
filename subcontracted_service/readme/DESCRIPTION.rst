This module allows a user to indicate that a service is subcontracted.
It provides the ability to create purchases from procurement processes.

This is a base module, upon specific modules for sale / manufacuturing, modules
will need to rely on. By itself it does not provide any function to the end user.

Possible uses of this module can be:

* Add subcontracted services to BOMs. When a manufacturing order is created a
  PO is triggered for the service to be subcontracted. See

* Add subcontracted services to sales order. When the SO is confirmed, it
  creates a PO for the service.
