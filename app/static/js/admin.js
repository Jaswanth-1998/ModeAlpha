document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".js-approve-user").forEach((button) => {
        button.addEventListener("click", async () => {
            const confirmMessage = button.dataset.confirmMessage || "Approve this user?";
            if (!window.confirm(confirmMessage)) {
                return;
            }

            const rowId = button.dataset.rowId;
            button.disabled = true;

            try {
                const response = await fetch(button.dataset.url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                });
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message || "Approval failed.");
                }

                const row = document.getElementById(rowId);
                if (row) {
                    row.remove();
                }

                if (window.showAppAlert) {
                    window.showAppAlert(data.message, "success");
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
