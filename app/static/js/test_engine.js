document.addEventListener("DOMContentLoaded", () => {
    const engine = document.querySelector("[data-test-engine='true']");
    if (!engine) {
        return;
    }

    const saveUrl = engine.dataset.saveAnswerUrl;
    const submitUrl = engine.dataset.submitUrl;
    const questionId = Number(engine.dataset.questionId);
    const timerDisplay = document.querySelector("#timerDisplay span");
    const autosaveStatus = document.getElementById("autosaveStatus");
    const pauseForm = document.querySelector(".js-pause-form");
    const answeredCounter = document.querySelector("[data-answered-counter='true']");
    const currentPaletteItem = document.querySelector(`[data-palette-question-id='${questionId}']`);
    let timeLeft = Number(engine.dataset.timeLeft || 0);
    let isSubmitting = false;

    const selectedOption = () => document.querySelector("input[name='selected_option']:checked")?.value || null;

    const updateTimer = () => {
        const minutes = String(Math.floor(timeLeft / 60)).padStart(2, "0");
        const seconds = String(timeLeft % 60).padStart(2, "0");
        timerDisplay.textContent = `${minutes}:${seconds}`;
    };

    const updateAnsweredCounter = () => {
        if (!answeredCounter) {
            return;
        }

        const totalQuestions = document.querySelectorAll("[data-palette-question-id]").length;
        const answeredQuestions = document.querySelectorAll(".palette-item.answered").length;
        answeredCounter.textContent = `${answeredQuestions}/${totalQuestions} answered`;
    };

    const updateCurrentPaletteState = (hasAnswer) => {
        if (!currentPaletteItem) {
            return;
        }

        currentPaletteItem.classList.toggle("answered", hasAnswer);
        currentPaletteItem.classList.remove("visited");
        updateAnsweredCounter();
    };

    const saveAnswer = async (navigateTo = null) => {
        try {
            autosaveStatus.textContent = "Saving answer...";
            const response = await fetch(saveUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question_id: questionId,
                    selected_option: selectedOption(),
                }),
            });
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || "Unable to save the answer.");
            }
            updateCurrentPaletteState(Boolean(data.selected_option));
            autosaveStatus.textContent = "Answer saved automatically.";
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

    if (pauseForm) {
        pauseForm.addEventListener("submit", async (event) => {
            if (event.defaultPrevented) {
                return;
            }
            event.preventDefault();
            autosaveStatus.textContent = "Saving answer and pausing test...";
            await saveAnswer();
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
