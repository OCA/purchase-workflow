from osv import fields,osv

class action_modal(osv.TransientModel):
    _name = "purchase.action_modal"
    _columns = {}
    def action(self, cr, uid, ids, context):
        for e in ('active_model','active_ids','action'):
            if e not in context:
                return False
        ids2=context['active_ids']
        context['active_ids']=ids
        context['active_id']=ids[0]
        res=getattr(self.pool.get(context['active_model']),context['action'])(cr, uid, ids2, context=context)
        if isinstance(res,dict):
            return res
        return {'type': 'ir.actions.act_window_close'}

class action_modal_datetime(osv.TransientModel):
    _name = "purchase.action_modal_datetime"
    _inherit = "purchase.action_modal"
    _columns = {
        'datetime': fields.datetime('Date'),
    }
