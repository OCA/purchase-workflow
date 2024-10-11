# Copyright 2024 Tecnativa - Víctor Martínez
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequestBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        request_user_group = "purchase_request.group_purchase_request_user"
        purchase_user_group = "purchase.group_purchase_user"
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="%s,%s" % (request_user_group, purchase_user_group),
        )
        request_manager_group = "purchase_request.group_purchase_request_manager"
        cls.manager_user = new_test_user(
            cls.env,
            login="test-manager-user",
            groups="%s,%s" % (request_manager_group, purchase_user_group),
        )
        cls.company = cls.env.company
        cls.company.purchase_request_approver_user_id = cls.manager_user
        cls.purchase_request_obj = cls.env["purchase.request"]
        cls.purchase_request_line_obj = cls.env["purchase.request.line"]
        cls.purchase_order = cls.env["purchase.order"]
        cls.wiz = cls.env["purchase.request.line.make.purchase.order"]
        cls.picking_type_id = cls.env.ref("stock.picking_type_in")
