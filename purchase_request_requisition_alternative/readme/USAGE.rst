Nothing to configure: the module installs itself as soon as both
``purchase_request`` and ``purchase_requisition`` are present, and works on
the standard flows.

* From an RFQ created out of a purchase request, use *Alternatives > Create
  Alternative*. The new RFQ is linked to the same request lines.
* From an RFQ, attach an existing one through *Alternatives*. Same result.

On the request line, the *Purchase Order Lines* field then lists the lines of
every alternative, so the request can be followed from any of them.
