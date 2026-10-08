from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_compare_lines_order_between_purchase_and_requistion(self):
        po = self.env.ref("purchase_requisition_section_and_note.po1")
        po._onchange_requisition_id()
        po_lines_order = [x.name for x in po.order_line.sorted("sequence")]
        requisition_lines_order = [
            x.name or x.product_id.display_name
            for x in po.requisition_id.line_with_sectionnote_ids.sorted("sequence")
        ]
        self.assertEqual(po_lines_order, requisition_lines_order)
