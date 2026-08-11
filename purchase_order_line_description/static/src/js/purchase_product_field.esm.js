/* Copyright 2026 Moduon
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {ProductLabelSectionAndNoteField} from "@account/components/product_label_section_and_note_field/product_label_section_and_note_field";
import {patch} from "@web/core/utils/patch";

patch(ProductLabelSectionAndNoteField.prototype, {
    parseLabel(value) {
        if (this.props.record.resModel === "purchase.order.line") {
            return value || "";
        }
        return super.parseLabel(value);
    },
});
