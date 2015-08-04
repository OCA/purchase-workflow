from . import models


def set_default_origin_address_id(cr, registry):
    cr.execute(
        """
        UPDATE product_pricelist pl
        SET origin_address_id = fap.supplier_id
        FROM framework_agreement_portfolio fap
        WHERE pl.portfolio_id = fap.id """)
