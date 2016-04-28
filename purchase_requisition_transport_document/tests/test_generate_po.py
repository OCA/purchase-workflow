from openerp.tests.common import TransactionCase


class TestPropagateDocuments(TransactionCase):
    def setUp(self):
        super(TestPropagateDocuments, self).setUp()

        self.Requisition = self.env['purchase.requisition']

        self.requisition = self.Requisition.new({})
        self.supplier = self.browse_ref('base.res_partner_1')

        self.doc1 = self.browse_ref('purchase_transport_document.CMR')
        self.doc2 = self.browse_ref(
            'purchase_transport_document.bill_of_lading')

    def test_it_propagates_no_documents(self):

        order_data = self.Requisition._prepare_purchase_order(self.requisition,
                                                              self.supplier)

        self.assertFalse(order_data.get('transport_document_ids'))

    def test_it_propagates_one_document(self):

        self.requisition.transport_document_ids = self.doc1

        order_data = self.Requisition._prepare_purchase_order(self.requisition,
                                                              self.supplier)

        self.assertEqual(
            order_data['transport_document_ids'],
            [(4, self.doc1.id)]
        )

    def test_it_propagates_two_documents(self):

        self.requisition.transport_document_ids = self.doc1 | self.doc2

        order_data = self.Requisition._prepare_purchase_order(self.requisition,
                                                              self.supplier)

        self.assertEqual(
            order_data['transport_document_ids'],
            [(4, self.doc1.id), (4, self.doc2.id)]
        )
