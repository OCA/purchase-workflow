/** @odoo-module **/

import {registry} from "@web/core/registry";
import {redirect} from "@web/core/utils/urls";

registry.category("web_tour.tours").add("purchase_signature", {
    url: "/my/rfq",
    steps: () => [
        {
            content: "open the test PO",
            trigger: "a:contains(/^test PO$/)",
            run: "click",
        },
        {
            content: "click sign",
            trigger: 'a:contains("Sign")',
            run: "click",
        },
        {
            content: "check submit is enabled",
            trigger: ".o_portal_sign_submit:enabled",
        },
        {
            trigger: ".modal .o_web_sign_name_and_signature input:value(Joel Willis)",
        },
        {
            content: "click select style",
            trigger: ".modal .o_web_sign_auto_select_style button",
            run: "click",
        },
        {
            content: "click style 4",
            trigger: ".o-dropdown-item:eq(3)",
            run: "click",
        },
        {
            content: "click submit",
            trigger: ".modal .o_portal_sign_submit:enabled",
            run: "click",
        },
        {
            content: "check it's confirmed",
            trigger: '#quote_content:contains("Thank You")',
            run: "click",
        },
        {
            trigger: "#quote_content",
            run: function () {
                redirect("/odoo");
            },
        },
        {
            trigger: "nav",
        },
    ],
});
