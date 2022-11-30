from odoo.fields import Date
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveCreate(TransactionCase):
    """
    # TEST 1 - Skip account move lines by key 'skip_record'
    """

    def setUp(self):
        super(TestAccountMoveCreate, self).setUp()

        self.product_vegetables = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_vegetables",
            raise_if_not_found=False,
        )
        self.product_tools = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_tools",
            raise_if_not_found=False,
        )
        self.partner_oleg = self.env.ref(
            "purchase_vendor_bill_breakdown.res_partner_test_demo_oleg",
            raise_if_not_found=False,
        )
        self.account_journal_id = (
            self.env["account.journal"]
            .create(
                {
                    "name": "Bank",
                    "type": "bank",
                    "code": "BNK67",
                    "company_id": self.env.user.company_id.id,
                }
            )
            .default_account_id.id
        )

        AccountMove = self.env["account.move"].with_context(
            default_move_type="in_refund",
            default_partner_id=self.partner_oleg.id,
            default_invoice_date=Date.from_string("2022-01-01"),
            default_currency_id=self.ref("base.EUR"),
        )

        account_move_test_1 = AccountMove.create(
            {
                "invoice_line_ids": [
                    self._prepare_account_move_line(self.product_vegetables.id, True),
                    self._prepare_account_move_line(self.product_tools.id),
                ],
            }
        )
        account_move_test_2 = AccountMove.create(
            {
                "invoice_line_ids": [
                    self._prepare_account_move_line(self.product_vegetables.id),
                    self._prepare_account_move_line(self.product_tools.id),
                ],
            }
        )
        account_move_test_3 = AccountMove.create(
            {
                "invoice_line_ids": [
                    self._prepare_account_move_line(self.product_vegetables.id, True),
                    self._prepare_account_move_line(self.product_tools.id, True),
                ],
            }
        )
        account_move_test_4 = AccountMove.create({})

        self.lines_count_1 = len(account_move_test_1.invoice_line_ids)
        self.lines_count_2 = len(account_move_test_2.invoice_line_ids)
        self.lines_count_3 = len(account_move_test_3.invoice_line_ids)
        self.lines_count_4 = len(account_move_test_4.invoice_line_ids)

    def _prepare_account_move_line(self, product_id, skip=False):
        line = {
            "quantity": 3,
            "price_unit": 300,
            "account_id": self.account_journal_id,
            "product_id": product_id,
        }
        if skip:
            line.update(skip_record=True)
        return 0, 0, line

    # TEST 1 - Skip account move lines by key 'skip_record'
    def test_account_move_skip_line_by_key(self):
        """Skip account move lines by key 'skip_record'"""
        self.assertEqual(
            self.lines_count_1,
            1,
            msg="Count invoice lines must be equal to 1",
        )
        self.assertEqual(
            self.lines_count_2,
            2,
            msg="Count invoice lines must be equal to 2",
        )
        self.assertEqual(
            self.lines_count_3,
            0,
            msg="Count invoice lines must be equal to 0",
        )
        self.assertEqual(
            self.lines_count_4,
            0,
            msg="Count invoice lines must be equal to 0",
        )
