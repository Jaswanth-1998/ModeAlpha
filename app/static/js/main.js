document.addEventListener("DOMContentLoaded", () => {
    const ensureFlashStack = () => {
        let flashStack = document.querySelector(".js-flash-stack");
        if (flashStack) {
            return flashStack;
        }

        const container = document.querySelector(".container-fluid.py-4") || document.body;
        flashStack = document.createElement("div");
        flashStack.className = "mb-4 js-flash-stack";
        container.prepend(flashStack);
        return flashStack;
    };

    const scheduleAlertDismiss = (alertElement) => {
        const dismissMs = Number(alertElement.dataset.dismissMs || 1000);

        window.setTimeout(() => {
            if (!alertElement.isConnected) {
                return;
            }

            const alertInstance = bootstrap.Alert.getOrCreateInstance(alertElement);
            alertInstance.close();
        }, dismissMs);
    };

    window.showAppAlert = (message, category = "success") => {
        const flashStack = ensureFlashStack();
        const alertElement = document.createElement("div");
        alertElement.className = `alert alert-${category} alert-dismissible fade show shadow-sm js-auto-dismiss-alert`;
        alertElement.setAttribute("role", "alert");
        alertElement.dataset.dismissMs = "1000";
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        flashStack.prepend(alertElement);
        scheduleAlertDismiss(alertElement);
    };

    document.querySelectorAll(".js-profile-password-field").forEach((input) => {
        input.value = "";
    });

    document.querySelectorAll(".js-auto-dismiss-alert").forEach((alertElement) => {
        scheduleAlertDismiss(alertElement);
    });

    document.querySelectorAll("form[data-confirm-message]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (event.defaultPrevented) {
                return;
            }

            const message = form.dataset.confirmMessage || "Are you sure you want to continue?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("a[data-confirm-message]").forEach((link) => {
        link.addEventListener("click", (event) => {
            const message = link.dataset.confirmMessage || "Are you sure you want to continue?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }

    const userMetricButton = document.querySelector(".js-refresh-user-metrics");
    if (userMetricButton) {
        userMetricButton.addEventListener("click", async () => {
            const metricsUrl = userMetricButton.dataset.metricsUrl;
            userMetricButton.disabled = true;

            try {
                const response = await fetch(metricsUrl);
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message || "Unable to refresh metrics.");
                }

                document.querySelector("[data-user-metric='available_tests']").textContent = data.metrics.available_tests;
                document.querySelector("[data-user-metric='attended_tests']").textContent = data.metrics.attended_tests;
                document.querySelector("[data-user-metric='average_marks']").textContent = data.metrics.average_marks;
            } catch (error) {
                window.showAppAlert(error.message, "danger");
            } finally {
                userMetricButton.disabled = false;
            }
        });
    }

    document.querySelectorAll(".js-toggle-section").forEach((toggle) => {
        const target = document.querySelector(toggle.dataset.target);
        if (!target) {
            return;
        }

        const syncVisibility = () => {
            target.classList.toggle("d-none", !toggle.checked);
        };

        syncVisibility();
        toggle.addEventListener("change", syncVisibility);
    });
});
