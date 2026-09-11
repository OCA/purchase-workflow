from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseComputeOrderMinPackage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplierinfo_model = cls.env["product.supplierinfo"]
        cls.cpo_model = cls.env["computed.purchase.order"]
        cls.cpol_model = cls.env["computed.purchase.order.line"]
        cls.product = cls.env.ref("product.product_product_4")
        cls.supplier = cls.env.ref("base.res_partner_2")

        # Create Supplierinfo with min and max nb of package
        cls.psi = cls.supplierinfo_model.create(
            {
                "partner_id": cls.supplier.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "min_nb_of_package": 2,
                "max_nb_of_package": 5,
                "package_qty": 10,
                "base_price": 100,
            }
        )

    def test_purchase_qty_package_exceeds_max(self):
        # Create a computed purchase order
        cpo = self.cpo_model.create(
            {
                "partner_id": self.supplier.id,
            }
        )
        # Create a computed purchase order line
        cpol = self.cpol_model.create(
            {
                "computed_purchase_order_id": cpo.id,
                "product_id": self.product.id,
                "psi_id": self.psi.id,
                "purchase_qty_package": 3,
                "uom_po_id": self.product.uom_id.id,
            }
        )
        # Try to set purchase_qty_package greater than max_nb_of_package
        with self.assertRaises(ValidationError):
            cpol.write({"purchase_qty_package": 6})
