/* Copyright 2026 Moduon
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("purchase_order_line_description_manual_edit", {
    steps: () => [
        {
            content: "Open the purchase order line editor",
            trigger:
                '.o_field_product_label_section_and_note_cell:contains("Purchase description for test product")',
            run: "click",
        },
        {
            content: "Edit the purchase order line description",
            trigger:
                ".o_selected_row .o_field_product_label_section_and_note_cell textarea",
            run: "edit Purchase description for test product test",
        },
        {
            content: "Save the edited purchase order line",
            trigger: ".oe_subtotal_footer",
            run: "click",
        },
        {
            content: "Wait for the line to leave inline edit mode",
            trigger: ".o_field_product_label_section_and_note_cell:not(:has(textarea))",
        },
        {
            content: "Save the purchase order",
            trigger: ".o_form_status_indicator .o_form_button_save:visible",
            run: "click",
        },
        {
            content: "Wait for the purchase order to save",
            trigger: ".o_form_status_indicator_buttons.invisible:not(:visible)",
        },
    ],
});
