This module extend purchase invoice plan to allow expanding (split) product lines by group name.

For example, a purchase order with 2 product lines, with 5 installment invoice plan.
Installment 1-3 set to group FY2021 and installment 4-5 set to FY2022.

Odoo will split 2 product lines into 4 product lines. Each 2 lines for each group.

When create invoice by plan,

* Installment 1-3 will create invoice from FY2021 product lines.
* Installment 4-5 will create invoice from FY2022 product lines.
