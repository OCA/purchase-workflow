odoo.define("purchase_order_report_selection.user_fields", function (require) {
    "use strict";

    var field_registry = require("web.field_registry");
    var relational_fields = require("web.relational_fields");
    var FieldMany2One = relational_fields.FieldMany2One;

    var ReportFields = FieldMany2One.extend({
        init: function () {
            this._super.apply(this, arguments);
        },
        _getDisplayfields: function () {
            const domain = [];
            var div_table = document.querySelector('div[name="order_line"]');
            const data_th = div_table.querySelectorAll("th");
            for (let i = 0; i < data_th.length; i++) {
                const item = data_th[i].dataset.name;
                if (item) {
                    domain.push(item);
                }
            }
            const optional_fields = div_table.querySelectorAll(
                'div[role="menu"] input[type="checkbox"]'
            );
            for (let i = 0; i < optional_fields.length; i++) {
                const item = optional_fields[i].name;
                if (domain.includes(item) === false) {
                    domain.push(item);
                }
            }
            return domain;
        },

        _renderEdit: function () {
            this.field.domain[1][2] = this._getDisplayfields();
            this._super.apply(this, arguments);
        },
    });
    field_registry.add("report_fields", ReportFields);
    return ReportFields;
});
