import openerp.tests.common as common


class test_purchase_requisition_line(common.TransactionCase):

    def setUp(self):
        super(test_purchase_requisition_line, self).setUp()
        self.reqLine = self.env.ref(
            'purchase_requisition.requisition_line1')

    def test_name_get(self):
        self.assertEqual(u'5.0 RAM SR5', self.reqLine.name_get()[0][1])
