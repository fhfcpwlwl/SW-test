const photoInput = document.getElementById("photo");
const fileNameLabel = document.getElementById("selectedFileName");
const optionCards = document.querySelectorAll(".option-card");

if (photoInput && fileNameLabel) {
    photoInput.addEventListener("change", () => {
        const [file] = photoInput.files;
        fileNameLabel.textContent = file ? file.name : "선택된 파일이 없습니다.";
    });
}

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

optionCards.forEach((card) => {
    const input = card.querySelector("input[type='radio']");
    if (!input) {
        return;
    }

    card.addEventListener("click", () => {
        updateOptionState(input.name);
    });

    input.addEventListener("change", () => {
        updateOptionState(input.name);
    });
});
