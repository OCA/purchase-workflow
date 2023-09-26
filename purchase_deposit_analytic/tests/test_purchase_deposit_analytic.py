# Copyright 2023 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.purchase_deposit.tests.test_purchase_deposit import TestPurchaseDeposit


class TestPurchaseDepositAnalytic(TestPurchaseDeposit):
    def setUp(self):
        super().setUp()
