odoo.define('employee_portal_suite.attendance_geo', function (require) {
    "use strict";

    // SAFETY CHECK → prevents running on homepage
    if (!$('.attendance_page').length) {
        return;
    }

    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');

    function showMessage(text, type = "success") {
        const box = $("#geo_message");
        box.removeClass("d-none alert-success alert-danger");
        box.addClass("alert-" + type);
        box.text(text);
    }

    function getLocationAndSend(url) {
        if (!navigator.geolocation) {
            showMessage("Geolocation is not supported by this browser.", "danger");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function (position) {
                ajax.jsonRpc(url, "call", {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                }).then(function (data) {
                    if (data.error) {
                        showMessage(data.error, "danger");
                    } else {
                        showMessage(data.message, "success");
                    }
                });
            },
            function () {
                showMessage("Unable to retrieve your location.", "danger");
            }
        );
    }

    publicWidget.registry.EmployeeAttendanceGeo = publicWidget.Widget.extend({
        selector: '.attendance_page',

        start: function () {
            this._super(...arguments);
            $("#btn_checkin").on("click", () => getLocationAndSend("/geo/checkin"));
            $("#btn_checkout").on("click", () => getLocationAndSend("/geo/checkout"));
        },
    });
});
