# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Camptocamp SA
#    Author: Leonardo Pistone
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    transport_document_ids = fields.Many2many(
        'transport.document',
        string="Transport Documents"
    )

    @api.model
    def _prepare_purchase_order(self, requisition, supplier):
        """Propagate transport documents from tender to RFQ"""

        values = super(PurchaseRequisition, self
                       )._prepare_purchase_order(requisition, supplier)
        values.update({
            'transport_document_ids': [
                (4, doc.id) for doc in requisition.transport_document_ids
            ],
        })
        return values
