openerp.purchase_requisition_multicurrency = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t;

    instance.web.purchase_requisition.CompareListView.include({
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            this.on('list_view_loaded', this, function() {
                if(self.$buttons.find('.oe_header_currency').length == 0){
                    new instance.web.Model('purchase.requisition')
                        .query(['currency_id'])
                        .filter([["id", "=", self.dataset.context.tender_id]]).first()
                        .done(function(tender) {
                            var currency_span = $('<br/><span class="oe_header_currency">All prices in currency of Call for Bids <b>['+tender['currency_id'][1]+']</b></span>');
                            self.$buttons.append(currency_span);
                        });
                }
            });
        },
    });

}
