User Permissions

1. Go to Settings > Users & Companies > Groups
2. Assign users to the "Manage Approved Suppliers" group to allow them to:
   - Create and manage approved supplier records
   - Override purchase order validations
   - Configure approved supplier requirements on categories and products
   - See approved supplier fields on product and partner forms

Product Category Configuration

1. Go to Products > Product Categories
2. Select a category and set "Require Approved Suppliers" to:
   - Checked: All products in this category require approved suppliers
   - Unchecked: Products in this category don't require approved suppliers

Product Exception Configuration

1. Go to Products > Product Templates
2. Open a product and go to the Purchase tab
3. Set "Approved Supplier Requirement" to:
   - "Use Category Setting": Follow the category configuration (default)
   - "Required": This product requires approved suppliers regardless of category
   - "Not Required": This product doesn't require approved suppliers regardless of category

4. The "Require Approved Suppliers" field shows the effective requirement based on:
   - Category setting
   - Product exception override
   - Computed result for easy verification
