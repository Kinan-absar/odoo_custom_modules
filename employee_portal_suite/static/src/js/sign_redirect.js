/** Final working redirect for Odoo 18 Sign */
odoo.define('employee_portal_suite.sign_redirect', function (require) {
    "use strict";

    let DocumentSignable;
    try {
        DocumentSignable = require("@sign/components/sign_request/document_signable");
    } catch (err) {
        // Not on a signing page → do nothing
        return;
    }

    if (!DocumentSignable || !DocumentSignable.default) {
        return;
    }

    const Original = DocumentSignable.default.prototype.onSignatureCompleted;

    DocumentSignable.default.prototype.onSignatureCompleted = async function () {

        // Wait for Odoo to finish saving the signature
        if (Original) {
            await Original.apply(this, arguments);
        }

        // Now redirect safely
        window.location.href = "/my/employee/sign";
    };
});
