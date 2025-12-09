/** Safe Signature Redirect Override for Odoo 18 */
odoo.define('employee_portal_suite.sign_redirect', function (require) {
    "use strict";

    let DocumentSignable;

    try {
        // Load ONLY inside sign page assets
        DocumentSignable = require("@sign/components/sign_request/document_signable");
    } catch (err) {
        // If module is missing (login, portal, etc.) → do nothing
        return;
    }

    if (!DocumentSignable || !DocumentSignable.default) {
        return;
    }

    const Original = DocumentSignable.default.prototype.onCompleteSignature;

    DocumentSignable.default.prototype.onCompleteSignature = function () {

        // Redirect employee portal after signing
        window.location.href = "/my/employee/sign";

        if (Original) {
            return Original.apply(this, arguments);
        }
    };
});
