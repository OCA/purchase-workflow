import {Component, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

/**
 * Renders purchase.order.sales_history_data (Json field) as a
 * year x month pivot table. Expected shape:
 * {
 *   "product_name": "...",
 *   "years": [2026, 2025, 2024],
 *   "months": ["Jan", "Feb", ..., "Dec"],
 *   "data": {"2026": [12, 0, 5, null, ...], "2025": [...], ...},
 * }
 * `null` means "no data yet" (future month of the current year);
 * distinct from 0, which means "no sales that month".
 */
export class PurchaseSalesHistoryField extends Component {
    static template = "purchase_line_sale_history.SalesHistoryField";
    static props = {...standardFieldProps};

    setup() {
        // Floats over the form (fixed to the viewport) so it stays visible
        // without scrolling no matter how many order lines are above it.
        // Anchored bottom-left: the chatter docks on the right (o-aside,
        // min 530px), so left avoids covering it. Collapsible so it
        // doesn't permanently sit over the lines being edited.
        this.state = useState({collapsed: false});
    }

    toggleCollapse() {
        this.state.collapsed = !this.state.collapsed;
    }

    get historyData() {
        const raw = this.props.record.data[this.props.name];
        if (!raw) {
            return null;
        }
        return typeof raw === "string" ? JSON.parse(raw) : raw;
    }

    get years() {
        return this.historyData?.years ?? [];
    }

    get months() {
        return this.historyData?.months ?? [];
    }

    /** 0-based index (Jan=0) of the current month, to highlight the header. */
    get currentMonthIndex() {
        return new Date().getMonth();
    }

    valueFor(year, monthIndex) {
        const row = this.historyData?.data?.[year];
        return row ? row[monthIndex] : null;
    }

    /** Max value across the whole pivot, used to scale heatmap intensity. */
    get maxValue() {
        // Start at 1 to avoid division by zero.
        let max = 1;
        for (const year of this.years) {
            for (const v of this.historyData?.data?.[year] ?? []) {
                if (v !== null && v > max) {
                    max = v;
                }
            }
        }
        return max;
    }

    /** 0..1 background intensity for a given cell, relative to maxValue. */
    intensityFor(year, monthIndex) {
        const v = this.valueFor(year, monthIndex);
        if (v === null) {
            return 0;
        }
        return Math.min(1, v / this.maxValue);
    }

    cellStyle(year, monthIndex) {
        const intensity = this.intensityFor(year, monthIndex);
        return `background-color: rgba(113, 75, 103, ${(intensity * 0.16).toFixed(3)});`;
    }

    rowTotal(year) {
        const row = this.historyData?.data?.[year] ?? [];
        return row.reduce((acc, v) => acc + (v ?? 0), 0);
    }

    colTotal(monthIndex) {
        return this.years.reduce(
            (acc, year) => acc + (this.valueFor(year, monthIndex) ?? 0),
            0
        );
    }

    get grandTotal() {
        return this.years.reduce((acc, year) => acc + this.rowTotal(year), 0);
    }
}

registry.category("fields").add("purchase_sales_history", {
    component: PurchaseSalesHistoryField,
    // Only makes sense as a readonly/inline widget, never in edition mode.
    supportedTypes: ["json", "jsonb"],
});
