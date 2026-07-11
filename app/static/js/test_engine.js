document.addEventListener("DOMContentLoaded", () => {
    const engine = document.querySelector("[data-test-engine='true']");
    if (!engine) {
        return;
    }

    const saveUrl = engine.dataset.saveAnswerUrl;
    const submitUrl = engine.dataset.submitUrl;
    const questionId = Number(engine.dataset.questionId);
    const unansweredToken = engine.dataset.unansweredToken || "__UNANSWERED__";
    const totalQuestions = Number(engine.dataset.totalQuestions || 0);
    const timerDisplay = document.querySelector("#timerDisplay span");
    const autosaveStatus = document.getElementById("autosaveStatus");
    const pauseForm = document.querySelector(".js-pause-form");
    const submitForm = document.getElementById("submitTestForm");
    const submitReadinessNote = document.getElementById("submitReadinessNote");
    const answeredCounter = document.querySelector("[data-answered-counter='true']");
    const currentPaletteItem = document.querySelector(`[data-palette-question-id='${questionId}']`);
    const markUnansweredButton = document.querySelector(".js-mark-unanswered");
    let timeLeft = Number(engine.dataset.timeLeft || 0);
    let isSubmitting = false;
    let currentResolutionState = engine.dataset.currentResolutionState || "unresolved";

    const selectedOption = () => document.querySelector("input[name='selected_option']:checked")?.value || null;

    const clearSelection = () => {
        document.querySelectorAll("input[name='selected_option']").forEach((input) => {
            input.checked = false;
        });
    };

    const updateTimer = () => {
        const minutes = String(Math.floor(timeLeft / 60)).padStart(2, "0");
        const seconds = String(Math.max(timeLeft % 60, 0)).padStart(2, "0");
        timerDisplay.textContent = `${minutes}:${seconds}`;
    };

    const updateAnsweredCounter = (answeredCount) => {
        if (!answeredCounter) {
            return;
        }

        answeredCounter.textContent = `${answeredCount}/${totalQuestions} answered`;
    };

    const updateCurrentPaletteState = (resolutionState) => {
        if (!currentPaletteItem) {
            return;
        }

        currentResolutionState = resolutionState;
        currentPaletteItem.dataset.resolutionState = resolutionState;
        currentPaletteItem.classList.remove("answered", "visited");

        if (resolutionState === "answered") {
            currentPaletteItem.classList.add("answered");
        } else if (resolutionState === "resolved-unanswered") {
            currentPaletteItem.classList.add("visited");
        }
    };

    const updateSubmitReadiness = (showFinalSubmit) => {
        if (submitForm) {
            submitForm.classList.toggle("d-none", !showFinalSubmit);
        }

        if (!submitReadinessNote) {
            return;
        }

        submitReadinessNote.textContent = showFinalSubmit
            ? "All questions are resolved. You can now use Final Submit."
            : "Final Submit appears only after every question is answered or marked as unanswered.";
    };

    const saveAnswer = async (
        navigateTo = null,
        explicitOption = undefined,
        successMessage = "Answer saved automatically."
    ) => {
        try {
            autosaveStatus.textContent = "Saving answer...";

            const submittedOption = explicitOption !== undefined
                ? explicitOption
                : (selectedOption() || (currentResolutionState === "resolved-unanswered" ? unansweredToken : null));

            const response = await fetch(saveUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question_id: questionId,
                    selected_option: submittedOption,
                }),
            });
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || "Unable to save the answer.");
            }

            if (data.is_marked_unanswered) {
                clearSelection();
            }

            updateCurrentPaletteState(data.resolution_state || "unresolved");
            updateAnsweredCounter(data.answered_count || 0);
            updateSubmitReadiness(Boolean(data.show_final_submit));
            autosaveStatus.textContent = successMessage;

            if (navigateTo) {
                window.location.href = navigateTo;
            }
            return true;
        } catch (error) {
            autosaveStatus.textContent = error.message;
            if (navigateTo) {
                window.location.href = navigateTo;
            }
            return false;
        }
    };

    document.querySelectorAll("input[name='selected_option']").forEach((input) => {
        input.addEventListener("change", () => saveAnswer());
    });

    document.querySelectorAll(".js-save-before-nav").forEach((link) => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            saveAnswer(link.href);
        });
    });

    if (markUnansweredButton) {
        markUnansweredButton.addEventListener("click", () => {
            clearSelection();
            saveAnswer(null, unansweredToken, "Question marked as unanswered.");
        });
    }

    if (pauseForm) {
        pauseForm.addEventListener("submit", async (event) => {
            if (event.defaultPrevented) {
                return;
            }

            event.preventDefault();
            autosaveStatus.textContent = "Saving answer and pausing test...";
            await saveAnswer(null);
            pauseForm.submit();
        });
    }

    const autoSubmit = async () => {
        if (isSubmitting) {
            return;
        }
        isSubmitting = true;

        try {
            autosaveStatus.textContent = "Submitting test...";
            const response = await fetch(submitUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || "Unable to submit the test.");
            }
            window.location.href = data.redirect_url;
        } catch (error) {
            autosaveStatus.textContent = error.message;
            isSubmitting = false;
        }
    };

    updateTimer();
    const timer = setInterval(() => {
        timeLeft -= 1;
        updateTimer();
        if (timeLeft <= 0) {
            clearInterval(timer);
            autoSubmit();
        }
    }, 1000);
});
