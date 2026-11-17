This module excludes RFQs pending to validate or validated when procuring a product.

If a RFQ, at some point, is requested to validate, it converts it immediately in something unmodifiable.
Then, taking this into account, if we procure a product with the same supplier as one open RFQ, it should
check if that is under validation or already validated and discard it on any of both cases.
