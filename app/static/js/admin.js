document.addEventListener("DOMContentLoaded", () => {
    const userActionButtons = document.querySelectorAll(".js-user-action");
    userActionButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const confirmMessage = button.dataset.confirmMessage || "Continue with this user action?";
            if (!window.confirm(confirmMessage)) {
                return;
            }

            const rowId = button.dataset.rowId;
            const alertType = button.dataset.alertType || "success";
            button.disabled = true;

            try {
                const response = await fetch(button.dataset.url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                });
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message || "The requested action could not be completed.");
                }

                const row = document.getElementById(rowId);
                if (row) {
                    const tbody = row.closest("tbody");
                    row.remove();

                    if (tbody && !tbody.querySelector("[id^='user-row-']")) {
                        const emptyRow = document.createElement("tr");
                        emptyRow.innerHTML = '<td colspan="6" class="text-center py-4 text-muted">There are no pending approvals.</td>';
                        tbody.appendChild(emptyRow);
                    }
                }

                if (window.showAppAlert) {
                    window.showAppAlert(data.message, alertType);
                }
            } catch (error) {
                if (window.showAppAlert) {
                    window.showAppAlert(error.message, "danger");
                } else {
                    window.alert(error.message);
                }
                button.disabled = false;
            }
        });
    });

    const refreshButton = document.querySelector(".js-refresh-admin-metrics");
    if (refreshButton) {
        refreshButton.addEventListener("click", async () => {
            refreshButton.disabled = true;

            try {
                const response = await fetch(refreshButton.dataset.analyticsUrl);
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message || "Unable to refresh admin metrics.");
                }

                document.querySelector("[data-admin-metric='total_users']").textContent = data.metrics.total_users;
                document.querySelector("[data-admin-metric='total_tests']").textContent = data.metrics.total_tests;
                document.querySelector("[data-admin-metric='users_attended']").textContent = data.metrics.users_attended;
                document.querySelector("[data-admin-metric='pending_approvals']").textContent = data.metrics.pending_approvals;
            } catch (error) {
                if (window.showAppAlert) {
                    window.showAppAlert(error.message, "danger");
                } else {
                    window.alert(error.message);
                }
            } finally {
                refreshButton.disabled = false;
            }
        });
    }
});
