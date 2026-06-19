* Go to *Purchase > Configuration > Purchase Auto Validation*.
* Create a rule: select one or more products, the supplier,
   and the weekday/hour at which matching draft purchase orders should be
   confirmed. Leave the company empty to apply the rule to all companies.
* When a sale triggers an automatic procurement for a
   configured product, it is routed to a dedicated purchase order shared
   by all sales matching the same rule, instead of being merged into the
   generic purchase order.
* Only the products configured on the rule can be added to that
   dedicated purchase order.
* The scheduled action *Auto Purchase Validation* confirms, every hour,
   any draft purchase order whose rule matches the current weekday and
   hour.
