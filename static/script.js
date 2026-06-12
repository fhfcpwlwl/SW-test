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

const productCards = Array.from(document.querySelectorAll("[data-product-card]"));
const routineStepTexts = Array.from(document.querySelectorAll(".routine-step-text"));
let activeProductCard = null;
let activeProductTimer = null;

function getProductAliases(card) {
    return [
        card.dataset.productName,
        card.dataset.productDisplayName,
        card.dataset.productTitle,
    ]
        .filter(Boolean)
        .map((alias) => alias.trim())
        .filter(Boolean)
        .sort((a, b) => b.length - a.length);
}

function findRoutineProductMatch(text) {
    const matches = [];

    productCards.forEach((card) => {
        getProductAliases(card).forEach((alias) => {
            const index = text.indexOf(alias);

            if (index >= 0) {
                matches.push({ card, alias, index });
            }
        });
    });

    return matches.sort((a, b) => b.alias.length - a.alias.length)[0] || null;
}

function highlightProductCard(card) {
    if (!card) {
        return;
    }

    if (activeProductCard && activeProductCard !== card) {
        activeProductCard.classList.remove("is-routine-highlight");
    }

    window.clearTimeout(activeProductTimer);
    activeProductCard = card;
    card.classList.add("is-routine-highlight");
    card.focus({ preventScroll: true });

    activeProductTimer = window.setTimeout(() => {
        card.classList.remove("is-routine-highlight");
        activeProductCard = null;
    }, 2800);
}

function scrollToProductCard(card) {
    const productSection = document.getElementById("productRecommendations");
    const target = productSection || card;

    target.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });

    window.setTimeout(() => {
        highlightProductCard(card);
    }, 520);
}

routineStepTexts.forEach((stepText) => {
    const originalText = stepText.textContent;
    const match = findRoutineProductMatch(originalText);

    if (!match) {
        return;
    }

    const illustration = stepText.closest("[data-routine-slide]")?.querySelector(".routine-action-svg");
    const actionClass = match.card.dataset.productKey ? `action-${match.card.dataset.productKey.replace(/_/g, "-")}` : "action-general";

    if (illustration) {
        Array.from(illustration.classList)
            .filter((className) => className.startsWith("action-"))
            .forEach((className) => illustration.classList.remove(className));
        illustration.classList.add(actionClass);
    }

    const beforeText = originalText.slice(0, match.index);
    const afterText = originalText.slice(match.index + match.alias.length);
    const productButton = document.createElement("button");

    productButton.type = "button";
    productButton.className = "routine-product-link";
    productButton.textContent = match.alias;
    productButton.setAttribute("aria-label", `${match.alias} 추천 제품 보기`);
    productButton.addEventListener("click", () => scrollToProductCard(match.card));

    stepText.replaceChildren(
        document.createTextNode(beforeText),
        productButton,
        document.createTextNode(afterText),
    );
});

const routineCarousels = Array.from(document.querySelectorAll("[data-routine-carousel]"));

routineCarousels.forEach((carousel) => {
    const slides = Array.from(carousel.querySelectorAll("[data-routine-slide]"));
    const currentLabel = carousel.querySelector("[data-routine-current]");
    const prevButton = carousel.querySelector("[data-routine-prev]");
    const nextButton = carousel.querySelector("[data-routine-next]");
    const dots = Array.from(carousel.querySelectorAll(".routine-step-dots span"));
    let currentIndex = 0;

    function showRoutineSlide(nextIndex) {
        if (!slides.length) {
            return;
        }

        currentIndex = (nextIndex + slides.length) % slides.length;

        slides.forEach((slide, index) => {
            slide.classList.toggle("is-hidden", index !== currentIndex);
        });

        dots.forEach((dot, index) => {
            dot.classList.toggle("is-active", index === currentIndex);
        });

        if (currentLabel) {
            currentLabel.textContent = String(currentIndex + 1);
        }
    }

    if (slides.length <= 1) {
        [prevButton, nextButton].forEach((button) => {
            if (button) {
                button.disabled = true;
            }
        });
    }

    if (prevButton) {
        prevButton.addEventListener("click", () => {
            showRoutineSlide(currentIndex - 1);
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", () => {
            showRoutineSlide(currentIndex + 1);
        });
    }

    showRoutineSlide(0);
});

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
