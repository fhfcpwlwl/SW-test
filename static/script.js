const photoInput = document.getElementById("photo");
const fileNameLabel = document.getElementById("selectedFileName");
const preview = document.getElementById("imagePreview");
const previewWrap = preview ? preview.closest(".preview-wrap") : null;
const form = document.getElementById("analysisForm");
const submitButton = document.getElementById("submitButton");

if (photoInput && fileNameLabel) {
    photoInput.addEventListener("change", () => {
        const [file] = photoInput.files;
        fileNameLabel.textContent = file ? file.name : "JPG, PNG, WEBP 파일을 업로드하세요.";

        if (!file || !preview || !previewWrap) {
            return;
        }

        const reader = new FileReader();
        reader.addEventListener("load", () => {
            preview.src = reader.result;
            previewWrap.classList.add("has-image");
        });
        reader.readAsDataURL(file);
    });
}

const surveyQuestions = Array.from(document.querySelectorAll(".scale-question"));
const submitPanel = document.querySelector(".submit-panel");

function scrollToNextSurveyStep(currentQuestion) {
    const currentIndex = surveyQuestions.indexOf(currentQuestion);
    const nextTarget = surveyQuestions[currentIndex + 1] || submitPanel;

    if (!nextTarget) {
        return;
    }

    window.setTimeout(() => {
        nextTarget.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }, 140);
}

surveyQuestions.forEach((question) => {
    question.addEventListener("change", (event) => {
        if (event.target.matches('input[type="radio"]')) {
            scrollToNextSurveyStep(question);
        }
    });
});

if (form && submitButton) {
    form.addEventListener("submit", () => {
        submitButton.classList.add("is-loading");
        submitButton.disabled = true;
        submitButton.textContent = "분석 중...";
    });
}
