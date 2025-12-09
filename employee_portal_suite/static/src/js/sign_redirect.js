/** Safe redirect override for Odoo 18 Sign (OWL patch) */
odoo.define('employee_portal_suite.sign_redirect', function (require) {
    "use strict";

    const { patch } = require("@web/core/utils/patch");
    let DocumentSignable;

    try {
        DocumentSignable = require("@sign/components/sign_request/document_signable").default;
    } catch (err) {
        // Not on sign page → exit safely
        return;
    }

    patch(DocumentSignable.prototype, "employee_portal_suite_redirect", {
        async onSignatureCompleted(...args) {

            // Run original behavior
            await this._super(...args);

            // Redirect AFTER signature is saved
            window.location.href = "/my/employee/sign";
        },
    });
});
