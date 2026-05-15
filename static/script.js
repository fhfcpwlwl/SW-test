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

document.querySelectorAll(".question-block input[type='radio']").forEach((input) => {
    input.addEventListener("change", () => {
        document
            .querySelectorAll(`input[name="${input.name}"]`)
            .forEach((radio) => {
                const label = radio.closest("label");
                if (label) {
                    label.classList.toggle("is-selected", radio.checked);
                }
            });
    });
});

if (form && submitButton) {
    form.addEventListener("submit", () => {
        submitButton.classList.add("is-loading");
        submitButton.disabled = true;
        submitButton.textContent = "분석 중...";
    });
}
