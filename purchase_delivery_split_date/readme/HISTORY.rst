12.0.2.1.0 (2020-04-30)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] when adding a new line on a confirmed PO, split the delivery (this was
  done only if a date was changed on an existing line)
* [IMP] when the quantity on a line is changed, the onchange would reset the
  planned date -> change this to prevent setting a date earlier than the one on
  the line, since if we are using this module the user probably has manually
  set the date first

12.0.2.0.0 (2020-04-10)
~~~~~~~~~~~~~~~~~~~~~~~

* Improve the module: when changing the date on a purchase line, this will
  cause a split or a merge of the pickings, to keep 1 picking per date.


11.0.1.0.0 (2018-09-16)
~~~~~~~~~~~~~~~~~~~~~~~

* Migration to 11.0.
  (`#461 <https://github.com/OCA/purchase-workflow/issues/461>`_)

* When the scheduled date is changed in the PO after confirmation the
  pickings are reorganized so as to force that every picking will have only
  moves to be delivered on the same date.
