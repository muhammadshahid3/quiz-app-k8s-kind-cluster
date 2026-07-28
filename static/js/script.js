// General site-wide JavaScript

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss alerts after 4 seconds
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });
});
