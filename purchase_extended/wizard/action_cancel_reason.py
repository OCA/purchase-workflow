from osv import fields,osv

class action_modal_cancelreason(osv.TransientModel):
    _name = "purchase.action_modal_cancelreason"
    _inherit = "purchase.action_modal"
    _columns = {
        'reason_id': fields.many2one('purchase.cancelreason', 'Reason for Cancellation', required=True),
    }
