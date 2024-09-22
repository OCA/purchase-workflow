The Purchase Order validation rules are configurable.
By default Purchase Order confirmation is prevented is the Vendor or Drop Ship Address
is not approvaed to be used in Purchase.

To configure Purchase Order validations navigate to
Purchase / Configuration / Purchase Exception Rules.
You need to belong to the Exception Manager security group to see this menu option.

For new vendor to require approval before being sold to, configure the Contact Stages
appropriately. For example:

* Navigate to Contacts / Configuration / Contact Stages
* Edit the "Active" stage: uncheck "Default Stage" and check "Approved for Purchase"
* Edit the "Draft" stage: check "Default Stage" and uncheck "Approved for Purchase"
