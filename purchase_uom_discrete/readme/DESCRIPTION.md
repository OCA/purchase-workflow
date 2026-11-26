Discrete and countable units cannot be split. Fractional values are meaningful
for continuous measures like weight, volume, length, or time, but not for
countable items such as units, boxes, or laptops.

This module rounds purchase order line quantities using Unit based UoMs UP to
the next whole number. UoMs that do not share the Unit(s) reference, such as kg,
liters, meters, or hours, keep fractional quantities.

This is only a purchase order form onchange helper, with no ORM-level create or
write enforcement, so users and integrations can still keep a fractional
quantity when it is intentionally applicable.
