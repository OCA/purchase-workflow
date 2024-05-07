/** @odoo-module **/

import tour from "web_tour.tour";

// This tour relies on data created on the Python test.
tour.register(
    "purchase_signature",
    {
        test: true,
        url: "/my/rfq",
    },
    [
        {
            content: "open the test PO",
            trigger: "a:containsExact('test PO')",
        },
        {
            content: "click sign",
            trigger: "a:contains('Sign')",
        },
        {
            content: "check submit is enabled",
            trigger: ".o_portal_sign_submit:enabled",
            run: function () {
                /**/
            },
        },
        {
            content: "click select style",
            trigger: ".o_web_sign_auto_select_style a",
        },
        {
            content: "click style 4",
            trigger: ".o_web_sign_auto_font_selection a:eq(3)",
        },
        {
            content: "click submit",
            trigger: ".o_portal_sign_submit:enabled",
        },
        {
            content: "check it's confirmed",
            trigger: "#quote_content:contains('Thank You')",
        },
        {
            trigger: "#quote_content",
            run: function () {
                window.location.href = window.location.origin + "/web";
            },
        },
        {
            trigger: "nav",
            run: function () {
                /**/
            },
        },
    ]
);
