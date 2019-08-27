You can set in settings another discount field to be applied.
For example, if we had `purchase_triple_discount`, we could set the general
discount in discount3 to be applied after all other discounts.

To do so:

#. Go to *Purchases > Configuration > Settings* and *Purchase Discount Field*
#. Select the discount you'd wish to use. `purchase_triple_discount` fields
   will appear when the module is installed.

There's a method at `res.company` called `_get_purchase_discount_fields` that
can be used to extend more line discount fields. For example, if we had the
field `discount4`, we could extend it like this:

.. code-block:: python

    @api.model
    def _get_purchase_discount_fields(self):
        discount_fields = super()._get_purchase_discount_fields()
        discount_fields += [('discount4', _('Discount 4'))]
        return discount_fields
