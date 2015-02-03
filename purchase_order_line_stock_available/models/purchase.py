
from openerp import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    virtual_available = fields.Float(related='product_id.virtual_available')
