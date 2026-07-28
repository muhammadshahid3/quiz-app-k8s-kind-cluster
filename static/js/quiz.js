// Quiz page JavaScript: elapsed-time counter + submit guard

document.addEventListener("DOMContentLoaded", function () {
    let seconds = 0;
    const display = document.getElementById("timer-display");

    if (display) {
        setInterval(function () {
            seconds++;
            const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
            const secs = String(seconds % 60).padStart(2, "0");
            display.textContent = `${mins}:${secs}`;
        }, 1000);
    }

    const form = document.getElementById("quiz-form");
    if (form) {
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector("button[type=submit]");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Submitting...';
            }
        });
    }
});
