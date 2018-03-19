odoo.define('purchase_order_barcode.PurchaseBarcodeHandler', function (require) {
    "use strict";
    var core = require('web.core');
    var Model = require('web.Model');
    var FormViewBarcodeHandler = require('barcodes.FormViewBarcodeHandler');
    var _t = core._t;
    var PurchaseBarcodeHandler = FormViewBarcodeHandler.extend({
        init: function (parent, context) {
            if (parent.ViewManager.action) {
                this.form_view_initial_mode = parent.ViewManager.action.context.form_view_initial_mode;
            } else if (parent.ViewManager.view_form) {
                this.form_view_initial_mode = parent.ViewManager.view_form.options.initial_mode;
            }
            this.m2x_field = 'pack_operation_product_ids';
            this.quantity_field = 'qty_done';
            return this._super.apply(this, arguments);
        },
        start: function () {
            this._super();
            this.po_model = new Model("purchase.order");
            this.form_view.options.disable_autofocus = 'true';
            if (this.form_view_initial_mode) {
                this.form_view.options.initial_mode = this.form_view_initial_mode;
            }
        },
        on_barcode_scanned: function(barcode) {
            var self = this;
            var po_id = self.view.datarecord.id
            var po_line_ids = self.view.datarecord.order_line
            self.po_model.call('po_barcode',[barcode, po_id]).then(function () {
                self.getParent().reload();
            });

        },
    });
    core.form_widget_registry.add('purchase_barcode_handler', PurchaseBarcodeHandler);
    return PurchaseBarcodeHandler;
});
