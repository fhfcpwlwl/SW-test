const photoInput = document.getElementById("photo");
const fileNameLabel = document.getElementById("selectedFileName");
const fileStatus = document.getElementById("fileStatus");
const optionCards = document.querySelectorAll(".option-card");
const progressCount = document.getElementById("progressCount");
const progressFill = document.getElementById("progressFill");
const submitButton = document.getElementById("submitButton");
const analysisForm = document.getElementById("analysisForm");

const questionNames = [
    "dry_oily_1",
    "dry_oily_2",
    "dry_oily_3",
    "sensitive_resistant_1",
    "sensitive_resistant_2",
    "sensitive_resistant_3",
    "pigmented_nonpigmented_1",
    "pigmented_nonpigmented_2",
    "pigmented_nonpigmented_3",
    "wrinkled_tight_1",
    "wrinkled_tight_2",
    "wrinkled_tight_3",
];

const updateOptionState = (name) => {
    const options = document.querySelectorAll(`input[name="${name}"]`);
    options.forEach((input) => {
        const card = input.closest(".option-card");
        if (!card) {
            return;
        }
        card.classList.toggle("is-selected", input.checked);
    });
};

const updateProgress = () => {
    const answered = questionNames.filter((name) => {
        const checked = document.querySelector(`input[name="${name}"]:checked`);
        return Boolean(checked);
    }).length;

    if (progressCount) {
        progressCount.textContent = `${answered} / ${questionNames.length}`;
    }

    if (progressFill) {
        progressFill.style.width = `${(answered / questionNames.length) * 100}%`;
    }
};

if (photoInput && fileNameLabel) {
    photoInput.addEventListener("change", () => {
        const [file] = photoInput.files;
        const label = file ? file.name : "선택된 파일이 없습니다.";
        fileNameLabel.textContent = label;
        if (fileStatus) {
            fileStatus.textContent = file ? "사진 선택이 완료되었습니다." : "아직 선택되지 않았습니다.";
        }
    });
}

optionCards.forEach((card) => {
    const input = card.querySelector("input[type='radio']");
    if (!input) {
        return;
    }

    card.addEventListener("click", () => {
        updateOptionState(input.name);
        updateProgress();
    });

    input.addEventListener("change", () => {
        updateOptionState(input.name);
        updateProgress();
    });
});

if (analysisForm && submitButton) {
    analysisForm.addEventListener("submit", () => {
        submitButton.classList.add("is-loading");
        submitButton.textContent = "분석 결과 생성 중...";
        submitButton.disabled = true;
    });
}

questionNames.forEach((name) => updateOptionState(name));
updateProgress();
