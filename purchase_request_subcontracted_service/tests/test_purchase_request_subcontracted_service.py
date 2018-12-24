# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestPurchaseRequestSubcontractedService(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestSubcontractedService, self).setUp()
        values = {'name': 'Service Subcontracted',
                  'type': 'service',
                  }
        self.subcontracted_service = self.env['product.product'].create(values)

    def test_service_has_purchase_request_route(self):
        self.subcontracted_service.purchase_request_service = True
        self.assertTrue(self.subcontracted_service.purchase_request)
        self.subcontracted_service.purchase_request = False
        self.assertFalse(self.subcontracted_service.purchase_request_service)
