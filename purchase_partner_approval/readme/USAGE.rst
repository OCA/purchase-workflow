To approve a Partner to be used in purchase:

* Edit the Partner form, and in the "Sales & Purchase" tab check the "Candidate to Purchase" box.
* Make sure the Parter is in a Stage that has the "Approved for Purchase" checkbox enabled.
  If this is the case, the Partner will automatically have enabled the "Can Purchase To" checkbox.
  found next to the "Candidate to Purchase" checkbox.

The "Candidate to Purchase" checkbox is only available in a draft/to approve Stage.
The "Can Purchase To" will only be set when moving to a Stage that is not draft/to approve.
Moving from an approved Stage to a draft one will not automatically reset the "Can Purchase To".
This means that removing from Can Purchase state also needs to go through an approval.

On a Purchase Order:

* The "Vendor" and "Drop Ship Address" selection lists
  only propose partners you "Can Purchase To".
* The CONFIRM button will show a blocking exception message if the selected Customeror
  Drop Ship Address do not have the "Can Purchase To" flag checked (this may vary depending
  how the exception rules are configured).
