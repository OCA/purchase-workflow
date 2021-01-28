# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, SavepointCase


class TestWorkAcceptanceLateFine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        account_obj = cls.env["account.account"]
        cls.service_product = cls.env.ref("product.product_product_1")
        cls.product_product = cls.env.ref("product.product_product_6")
        cls.res_partner = cls.env.ref("base.res_partner_3")
        cls.employee = cls.env.ref("base.user_demo")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")
        cls.main_company = cls.env.ref("base.main_company")
        cls.env.cr.execute(
            """UPDATE res_company SET currency_id = %s
            WHERE id = %s""",
            (cls.main_company.id, cls.currency_eur.id),
        )
        cls.date_now = fields.Datetime.now()
        cls.account_receivable = account_obj.create(
            {
                "code": "cust_acc",
                "name": "customer account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.not_late = cls.date_now + relativedelta(days=2)
        cls.late2days = cls.date_now - relativedelta(days=2)

        # Enable and Config WA Delivery Late Fines
        cls._config_wa_late(cls)

    def _config_wa_late(self):
        config = self.env["res.config.settings"]
        with Form(config) as c:
            c.group_enable_fines_on_wa = True
            c.wa_fines_rate = 100.0
            c.wa_fines_late_account_id = self.account_receivable

    def _create_wa(self, due_date, currency=False, product_qty=False):
        work_acceptance = self.env["work.acceptance"].create(
            {
                "partner_id": self.res_partner.id,
                "responsible_id": self.employee.id,
                "date_due": due_date,
                "date_receive": self.date_now,
                "company_id": self.main_company.id,
                "currency_id": currency or self.currency_eur.id,
                "wa_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_product.id,
                            "name": self.service_product.name,
                            "price_unit": self.service_product.standard_price,
                            "product_qty": product_qty or 1.0,
                            "product_uom": self.service_product.uom_id.id,
                        },
                    )
                ],
            }
        )
        work_acceptance._onchange_late_days()
        work_acceptance._onchange_fines_late()
        return work_acceptance

    def test_01_compute_wa_late(self):
        work_acceptance = self._create_wa(self.not_late)
        self.assertEqual(work_acceptance.late_days, 0)
        work_acceptance = self._create_wa(self.late2days)
        self.assertEqual(work_acceptance.late_days, 2)
        self.assertEqual(work_acceptance.fines_rate, 100.0)
        self.assertEqual(work_acceptance.fines_late, 200.0)

    def test_02_wa_late_multi_currency(self):
        work_acceptance = self._create_wa(
            self.late2days, self.currency_usd.id, product_qty=2
        )
        self.assertEqual(work_acceptance.currency_id.id, self.currency_usd.id)
        move = self.env["account.move"].create({"move_type": "out_invoice"})
        self.assertEqual(move.currency_id.id, self.currency_eur.id)
        with Form(move) as m:
            m.partner_id = self.res_partner
            m.late_wa_id = work_acceptance
        move = m.save()
        self.assertEqual(move.currency_id.id, self.currency_usd.id)

    def test_03_create_fines_from_wa(self):
        work_acceptance1 = self._create_wa(self.late2days)
        work_acceptance2 = self._create_wa(self.not_late)
        result = work_acceptance1.action_create_fines_invoice()
        # Should be form view
        move = self.env[result["res_model"]].browse(result["res_id"])
        self.assertEqual(move.late_wa_id.id, work_acceptance1.id)
        self.assertEqual(len(work_acceptance1.fines_invoice_ids.ids), 1)
        self.assertEqual(work_acceptance1.fines_invoice_count, 1)
        # Can create 1 time until you cancel fines invoice
        with self.assertRaises(UserError):
            work_acceptance1.action_create_fines_invoice()
        move.button_cancel()
        work_acceptance1.action_create_fines_invoice()
        self.assertEqual(len(work_acceptance1.fines_invoice_ids.ids), 2)
        self.assertEqual(work_acceptance1.fines_invoice_count, 2)
        # Not late can't create fines
        with self.assertRaises(UserError):
            work_acceptance2.action_create_fines_invoice()
        # Button from wa to fines
        work_acceptance1.action_view_invoice()

    def test_04_create_multi_fines_from_wa(self):
        work_acceptance1 = self._create_wa(self.late2days)
        work_acceptance2 = self._create_wa(self.late2days)
        ctx = {"active_ids": [work_acceptance1.id, work_acceptance2.id]}
        work_acceptance = work_acceptance1 + work_acceptance2
        result = work_acceptance.with_context(ctx).action_create_fines_invoice()
        # Should be tree view
        self.assertEqual(result["res_id"], 0)
        domain = result["domain"]
        move_ids = self.env[result["res_model"]].browse(domain[0][2])
        self.assertEqual(move_ids.mapped("late_wa_id").ids, work_acceptance.ids)
