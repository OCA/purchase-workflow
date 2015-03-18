openerp.purchase_requisition_bid_selection = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t;

    instance.web.purchase_requisition.CompareListView.include({
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            this.on('list_view_loaded', this, function() {
                if(self.$buttons.find('.oe_close_bid').length == 0){
                    var button = $("<button type='button' class='oe_button oe_highlight oe_close_bid'>Confirm Selection</button>")
                        .click(this.proxy('close_bids_selection'));
                    button.after('<span class="oe_fade" style="margin:0 4px">or</span>');
                    button.after($('<a accesskey="D" class="oe_bold oe_form_button_cancel" href="#">Close</a>')
                        .click(function(){self.do_action('history_back')}));
                    self.$buttons.append(button);
                }
                self.$buttons.find('.oe_generate_po').remove();
            });
        },
        close_bids_selection: function () {
            var self = this;
            new instance.web.Model('purchase.requisition').call("confirm_selection",[self.dataset.context.tender_id,self.dataset.context]).then(function(result) {
                self.do_action(result,{on_close:function(){self.do_action('history_back')}});
            });
        },
    });

}
