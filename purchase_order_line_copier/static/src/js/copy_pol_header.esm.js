import {FormController} from "@web/views/form/form_controller";
import {ViewButton} from "@web/views/view_button/view_button";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

function getSelectedLineIds(record, rootEl) {
    const list = record?.data?.order_line;
    if (list) {
        if (list.selection?.length) {
            const modelIds = list.selection
                .map((r) => r.resId)
                .filter((id) => typeof id === "number" && !Number.isNaN(id));
            if (modelIds.length) {
                return modelIds;
            }
        }
        const selectedFromRecords = list.records
            ? list.records
                  .filter((r) => r.selected)
                  .map((r) => r.resId)
                  .filter((id) => typeof id === "number" && !Number.isNaN(id))
            : [];
        if (selectedFromRecords.length) {
            return selectedFromRecords;
        }
    }
    if (!rootEl) {
        return [];
    }
    const orderLineField = rootEl.querySelector('.o_field_widget[name="order_line"]');
    if (!orderLineField) {
        return [];
    }
    const ids = [];
    const selectedRows = orderLineField.querySelectorAll(
        "tr.o_data_row.o_selected_row, tr.o_data_row.o_data_row_selected"
    );
    selectedRows.forEach((row) => {
        const domId = row && row.dataset ? row.dataset.id : null;
        if (domId && list?.records) {
            const rec = list.records.find((r) => String(r.id) === String(domId));
            const rid = rec && rec.resId;
            if (typeof rid === "number" && !Number.isNaN(rid)) {
                ids.push(rid);
            }
        } else if (domId) {
            const parsed = parseInt(domId, 10);
            if (!Number.isNaN(parsed)) {
                ids.push(parsed);
            }
        }
    });
    if (!ids.length) {
        const checked = orderLineField.querySelectorAll(
            "input.o_list_record_selector:checked"
        );
        checked.forEach((checkbox) => {
            const row = checkbox.closest("tr");
            const domId = row && row.dataset ? row.dataset.id : null;
            if (domId && list?.records) {
                const rec = list.records.find((r) => String(r.id) === String(domId));
                const rid = rec && rec.resId;
                if (typeof rid === "number" && !Number.isNaN(rid)) {
                    ids.push(rid);
                }
            } else if (domId) {
                const parsed = parseInt(domId, 10);
                if (!Number.isNaN(parsed)) {
                    ids.push(parsed);
                }
            }
        });
    }
    return ids;
}

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
    },

    _getSelectedPurchaseLineIds() {
        return getSelectedLineIds(this.model?.root, this.el);
    },

    async onButtonClicked(ev) {
        const attrs = ev?.data?.attrs || {};
        const record = this.model?.root;
        if (
            record?.resModel === "purchase.order" &&
            attrs.name === "action_open_copy_lines_wizard"
        ) {
            const selectedLineIds = this._getSelectedPurchaseLineIds();
            const ctx = {
                default_order_id: record.resId,
                active_model: "purchase.order.line",
                active_id: (selectedLineIds && selectedLineIds[0]) || false,
                active_ids: selectedLineIds || [],
                active_line_ids: selectedLineIds || [],
            };
            if (selectedLineIds && selectedLineIds.length) {
                ctx.default_line_ids = [[6, 0, selectedLineIds]];
            }
            await this.actionService.doAction({
                name: "Copy Purchase Lines",
                type: "ir.actions.act_window",
                res_model: "copy.purchase.line.wizard",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: ctx,
            });
            return;
        }
        return super.onButtonClicked(ev);
    },
});

patch(X2ManyField.prototype, {
    get rendererProps() {
        const props = super.rendererProps;
        if (this.props?.crudOptions?.allow_selectors) {
            props.allowSelectors = true;
        }
        return props;
    },
});

patch(ViewButton.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    async onClick(ev, newWindow) {
        const clickParams = this.clickParams || {};
        const record = this.props.record;
        if (
            record?.resModel === "purchase.order" &&
            clickParams.name === "action_open_copy_lines_wizard"
        ) {
            const rootEl = document.querySelector(".o_form_view");
            let selectedLineIds = getSelectedLineIds(record, rootEl);
            if (record?.save) {
                await record.save({reload: false});
                const refreshedIds = getSelectedLineIds(record, rootEl);
                if (refreshedIds.length) {
                    selectedLineIds = refreshedIds;
                }
            }
            const ctx = {
                default_order_id: record.resId,
                active_model: "purchase.order.line",
                active_id: selectedLineIds[0] || false,
                active_ids: selectedLineIds || [],
                active_line_ids: selectedLineIds || [],
            };
            if (selectedLineIds && selectedLineIds.length) {
                ctx.default_line_ids = [
                    [6, 0, selectedLineIds.filter((id) => typeof id === "number")],
                ];
            }
            this.actionService.doAction({
                name: "Copy Purchase Lines",
                type: "ir.actions.act_window",
                res_model: "copy.purchase.line.wizard",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: ctx,
            });
            return;
        }
        return super.onClick(ev, newWindow);
    },
});
