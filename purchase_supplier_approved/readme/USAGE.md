Managing Approved Suppliers

1. Go to Purchase > Products > Approved Suppliers
2. Create new approved supplier records with:
   - Supplier (Partner)
   - Product Template
   - Valid From date
   - Valid To date (optional)
   - Active status

From Product Template

1. Open any product template
2. Click the "Approved Suppliers" smart button to view/manage approvals for that product
3. In the Purchase tab, you can:
   - Configure the approved supplier requirement (override category setting)
   - View the effective requirement (computed field)
   - Directly add approved suppliers (if you have the right permissions)

Understanding Effective Requirements

The system determines if approved suppliers are required based on:

1. **Product Exception**: If set to "Required" or "Not Required", this overrides the category
2. **Category Setting**: If no product exception, uses the category configuration
3. **Default**: If no category is set, approved suppliers are not required

The "Require Approved Suppliers" field on products shows the computed result for easy verification.

From Partner

1. Open any supplier partner
2. Click the "Approved Products" smart button to view/manage products for which this partner is approved
3. In the Purchase tab, you can also directly add approved products (if you have the right permissions)

Purchase Order Validation

1. When creating purchase orders, the system will:
   - Show warnings when adding products with unapproved suppliers
   - Display a warning banner if the PO contains unapproved suppliers
   - Block confirmation if any product has an unapproved supplier

2. Users with "Manage Approved Suppliers" permissions can:
   - Enable "Override Supplier Approval" checkbox
   - Provide a mandatory reason for the override
   - Confirm the purchase order despite unapproved suppliers
