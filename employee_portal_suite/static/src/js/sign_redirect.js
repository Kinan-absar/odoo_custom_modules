/** Sign Redirect Override - Only working method in Odoo 18 */
odoo.define('employee_portal_suite.sign_redirect', function (require) {
    "use strict";

    const DocumentSignable = require("@sign/components/sign_request/document_signable");

    // Save original handler
    const originalHandler = DocumentSignable.default.prototype.onCompleteSignature;

    // Override
    DocumentSignable.default.prototype.onCompleteSignature = function () {

        // 🔥 TODO — change redirect target here:
        window.location.href = "/my/employee/sign";

        // Keep original behavior
        if (originalHandler) {
            originalHandler.apply(this, arguments);
        }
    };
});
