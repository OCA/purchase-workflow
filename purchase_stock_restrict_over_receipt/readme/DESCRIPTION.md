This module blocks the validation of a receipt that would leave a purchase
order line received beyond its ordered quantity.

Odoo accepts any quantity on a receipt: the excess is added to the received
quantity of the order line, and a product that was not ordered gets a new
order line with no ordered quantity. Whatever is derived from the received
quantity, such as a vendor bill on received quantities, then follows the
receipt rather than the order.

With this module the order has to be updated first, so that an excess is
agreed on the order before it enters the stock.
