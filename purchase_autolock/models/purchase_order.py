# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def autolock_purchase(self):
        """
        This will just lock the purchase. But can be extended to do more things.
        """
        self.ensure_one()
        self.button_done()

    def can_be_locked(self):
        """
        Dummy method to exlcude POS to be locked under some criteria
        """
        self.ensure_one()
        days = self.company_id.number_of_day_lock_po
        if not days:
            days = 31
        min_date_dt = datetime.today() - relativedelta(days=days)
        last_updated_date = sorted(self.message_ids, key=lambda l: (l["write_date"]))[
            -1
        ].write_date
        if last_updated_date > min_date_dt:
            return False
        else:
            return True

    @api.model
    def cron_auto_lock_purchase(self):
        autolock_domain = self.get_po_autolock_domain()
        purchases_to_lock = self.search(autolock_domain, limit=100)
        for po in purchases_to_lock.filtered(lambda a: a.can_be_locked()):
            _logger.info("Locking %s" % po.name)
            po.autolock_purchase()
            po.afterlock_purchase()

    def afterlock_purchase(self):
        """Dummy method to perform actions after the locking"""
        self.ensure_one()

    @api.model
    def get_po_autolock_domain(self):
        """
        The domain for PO to be locked. This can be extended if using third module
        that gets a search on the shipment status
        """
        return [
            ("state", "=", "purchase"),
            ("invoice_status", "=", "invoiced"),
        ]
