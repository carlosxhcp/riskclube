document.addEventListener("DOMContentLoaded", function () {
    const mainImage = document.getElementById("mainProductImage");
    const thumbsContainer = document.querySelector(".product-thumbs");
    const colorButtons = document.querySelectorAll(".color-dot");

    const selectedColorName = document.getElementById("selectedColorName");
    const selectedSizeName = document.getElementById("selectedSizeName");
    const sizeOptions = document.querySelector(".size-options");

    const prevBtn = document.getElementById("prevImage");
    const nextBtn = document.getElementById("nextImage");

    const customNameInput = document.getElementById("customName");
    const customNameLimitText = document.getElementById("customNameLimitText");
    const bottleNamePreview = document.getElementById("bottleNamePreview");

    const bottleViewButtons = document.querySelectorAll(".bottle-view-btn");
    const productMainImageBox = document.querySelector(".product-main-image");
    const engravingSideButtons = document.querySelectorAll(".engraving-side-btn");
    const directionButtons = document.querySelectorAll(".name-direction-btn");

    const showCustomNameBtn = document.getElementById("showCustomNameBtn");
    const customNameQuestion = document.getElementById("customNameQuestion");
    const customNameFields = document.getElementById("customNameFields");

    const fontButtons = document.querySelectorAll(".name-font-btn");

    let currentImages = [];
    let currentIndex = 0;
    let currentBottleView = "front";

    let selectedEngravingSide =
        document.querySelector(".engraving-side-btn.active")?.dataset.engravingSide || "front";

    let selectedNameDirection =
        document.querySelector(".name-direction-btn.active")?.dataset.direction || "vertical";

    let selectedNameFont =
        document.querySelector(".name-font-btn.active")?.dataset.font || "'Arial', sans-serif";

    function applyNameFont() {
        if (!bottleNamePreview) return;
        bottleNamePreview.style.fontFamily = selectedNameFont;
    }

    function updateNamePreviewVisibility() {
        if (!bottleNamePreview) return;

        bottleNamePreview.style.display =
            currentBottleView === selectedEngravingSide ? "block" : "none";
    }

    function applyNameDirection() {
        if (!customNameInput || !bottleNamePreview) return;

        const isHorizontal = selectedNameDirection === "horizontal";

        customNameInput.maxLength = isHorizontal ? 5 : 15;

        if (customNameLimitText) {
            customNameLimitText.textContent = isHorizontal
                ? "Máximo de 5 caracteres"
                : "Máximo de 15 caracteres";
        }

        bottleNamePreview.classList.toggle("horizontal", isHorizontal);
        bottleNamePreview.classList.toggle("vertical", !isHorizontal);
    }

    function applyResponsiveFontSize(value) {
        if (!bottleNamePreview) return;

        const length = value.length;
        const isMobile = window.innerWidth <= 480;
        const isTablet = window.innerWidth <= 768 && window.innerWidth > 480;

        if (selectedNameDirection === "vertical") {
            let size = isMobile ? 18 : isTablet ? 21 : 24;

            if (length >= 8) size -= 1;
            if (length >= 10) size -= 1;
            if (length >= 12) size -= 1;
            if (length >= 14) size -= 1;
            if (length >= 15) size -= 1;

            bottleNamePreview.style.fontSize = Math.max(isMobile ? 13 : 18, size) + "px";
            bottleNamePreview.style.letterSpacing = isMobile ? ".5px" : "1.5px";
        } else {
            let size = isMobile ? 17 : isTablet ? 20 : 24;

            if (length >= 3) size -= 2;
            if (length >= 4) size -= 2;
            if (length >= 5) size -= 2;

            bottleNamePreview.style.fontSize = Math.max(isMobile ? 12 : 16, size) + "px";
            bottleNamePreview.style.letterSpacing = isMobile ? ".4px" : "1px";
        }
    }

    function updateNamePreviewText() {
        if (!customNameInput || !bottleNamePreview) return;

        const maxLength = selectedNameDirection === "horizontal" ? 5 : 15;

        let value = customNameInput.value.trim().toUpperCase();

        if (value.length > maxLength) {
            value = value.substring(0, maxLength);
            customNameInput.value = value;
        }

        bottleNamePreview.textContent = value;

        applyNameDirection();
        applyResponsiveFontSize(value);
        applyNameFont();
        updateNamePreviewVisibility();
    }

    function setActiveThumb(index) {
        document.querySelectorAll(".thumb").forEach(thumb => {
            thumb.classList.remove("active");
        });

        const thumbs = document.querySelectorAll(".thumb");

        if (thumbs[index]) {
            thumbs[index].classList.add("active");
        }
    }

    function setBottleView(view) {
        const backImage = productMainImageBox?.dataset.backImage;

        if (view === "front") {
            currentBottleView = "front";
            currentIndex = 0;

            mainImage.src =
                currentImages[0] ||
                productMainImageBox?.dataset.frontImage ||
                mainImage.src;

            mainImage.classList.remove("gallery-fill");
            setActiveThumb(0);
        }

        if (view === "back" && backImage) {
            currentBottleView = "back";
            currentIndex = 1;

            mainImage.src = backImage;
            mainImage.classList.remove("gallery-fill");
            setActiveThumb(1);
        }

        bottleViewButtons.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.view === currentBottleView);
        });

        updateNamePreviewVisibility();
    }

    function updateMainImage(index) {
        if (!mainImage || !currentImages.length) return;

        if (index < 0) {
            currentIndex = currentImages.length - 1;
        } else if (index >= currentImages.length) {
            currentIndex = 0;
        } else {
            currentIndex = index;
        }

        mainImage.src = currentImages[currentIndex];

        const backImage = productMainImageBox?.dataset.backImage;

        const isExtraGalleryImage = backImage
            ? currentIndex >= 2
            : currentIndex >= 1;

        mainImage.classList.toggle("gallery-fill", isExtraGalleryImage);

        if (currentIndex === 0) {
            currentBottleView = "front";

            bottleViewButtons.forEach(btn => {
                btn.classList.toggle("active", btn.dataset.view === "front");
            });
        } else if (currentIndex === 1 && backImage) {
            currentBottleView = "back";

            bottleViewButtons.forEach(btn => {
                btn.classList.toggle("active", btn.dataset.view === "back");
            });
        } else {
            currentBottleView = "gallery";

            bottleViewButtons.forEach(btn => {
                btn.classList.remove("active");
            });
        }

        setActiveThumb(currentIndex);
        updateNamePreviewVisibility();
    }

    function renderGallery(images) {
        if (!thumbsContainer || !images.length) return;

        const backImage = productMainImageBox?.dataset.backImage;

        currentImages = [];

        if (images[0]) {
            currentImages.push(images[0]);
        }

        if (backImage) {
            currentImages.push(backImage);
        }

        images.slice(1).forEach(imageUrl => {
            currentImages.push(imageUrl);
        });

        currentIndex = 0;
        thumbsContainer.innerHTML = "";

        currentImages.forEach((imageUrl, index) => {
            const button = document.createElement("button");

            button.type = "button";
            button.className = backImage
                ? (index <= 1 ? "thumb" : "thumb gallery-fill")
                : (index === 0 ? "thumb" : "thumb gallery-fill");

            if (index === 0) {
                button.classList.add("active");
            }

            button.innerHTML = `<img src="${imageUrl}" alt="{{ product.name }}">`;

            button.addEventListener("click", function () {
                updateMainImage(index);
            });

            thumbsContainer.appendChild(button);
        });

        updateMainImage(0);
    }

    function renderSizes(sizes) {
        if (!sizeOptions) return;

        sizeOptions.innerHTML = "";

        if (!sizes || !sizes.length) {
            sizes = [{ name: "900ML" }];
        }

        sizes.forEach((size, index) => {
            const button = document.createElement("button");

            button.type = "button";
            button.className = "size-btn";
            button.dataset.sizeName = size.name;
            button.innerText = size.name;

            if (index === 0) {
                button.classList.add("active");
            }

            button.addEventListener("click", function () {
                document.querySelectorAll(".size-btn").forEach(btn => {
                    btn.classList.remove("active");
                });

                this.classList.add("active");

                if (selectedSizeName) {
                    selectedSizeName.textContent = size.name;
                }
            });

            sizeOptions.appendChild(button);
        });

        if (selectedSizeName) {
            selectedSizeName.textContent = sizes[0].name;
        }
    }

    if (showCustomNameBtn && customNameQuestion && customNameFields) {
        showCustomNameBtn.addEventListener("click", function () {
            customNameQuestion.classList.add("hide");

            setTimeout(() => {
                customNameQuestion.style.display = "none";
                customNameFields.classList.add("show");

                if (customNameInput) {
                    customNameInput.focus();
                }

                updateNamePreviewText();
            }, 250);
        });
    }

    fontButtons.forEach(button => {
        button.addEventListener("click", function () {
            fontButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            selectedNameFont = this.dataset.font || "'Arial', sans-serif";

            applyNameFont();
            updateNamePreviewText();
        });
    });

    if (customNameInput && bottleNamePreview) {
        customNameInput.addEventListener("input", updateNamePreviewText);
    }

    directionButtons.forEach(button => {
        button.addEventListener("click", function () {
            directionButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            selectedNameDirection = this.dataset.direction || "vertical";

            applyNameDirection();
            updateNamePreviewText();
        });
    });

    bottleViewButtons.forEach(button => {
        button.addEventListener("click", function () {
            setBottleView(this.dataset.view);
        });
    });

    engravingSideButtons.forEach(button => {
        button.addEventListener("click", function () {
            engravingSideButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            selectedEngravingSide = this.dataset.engravingSide || "front";

            if (selectedEngravingSide === "front") {
                setBottleView("front");
            }

            if (selectedEngravingSide === "back") {
                setBottleView("back");
            }

            updateNamePreviewVisibility();
        });
    });

    colorButtons.forEach(button => {
        button.addEventListener("click", function () {
            const colorName = this.dataset.colorName || "";

            let images = [];
            let sizes = [];

            try {
                images = JSON.parse(this.dataset.images);
            } catch (error) {
                images = [];
            }

            try {
                sizes = JSON.parse(this.dataset.sizes);
            } catch (error) {
                sizes = [];
            }

            colorButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            if (selectedColorName) {
                selectedColorName.textContent = colorName;
            }

            renderGallery(images);
            renderSizes(sizes);
        });
    });

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            updateMainImage(currentIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            updateMainImage(currentIndex + 1);
        });
    }

    window.addEventListener("resize", updateNamePreviewText);

    const firstColorButton = document.querySelector(".color-dot.active");

    if (firstColorButton) {
        let firstImages = [];
        let firstSizes = [];

        try {
            firstImages = JSON.parse(firstColorButton.dataset.images);
        } catch (error) {
            firstImages = [];
        }

        try {
            firstSizes = JSON.parse(firstColorButton.dataset.sizes);
        } catch (error) {
            firstSizes = [];
        }

        if (selectedColorName) {
            selectedColorName.textContent = firstColorButton.dataset.colorName || "";
        }

        renderGallery(firstImages);
        renderSizes(firstSizes);
    }

    applyNameDirection();
    updateNamePreviewText();
    updateNamePreviewVisibility();
});
</script>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const addCartBtn = document.getElementById("addCartBtn");
    const buyNowBtn = document.getElementById("buyNowBtn");

    if (!addCartBtn) return;

    let addingToCart = false;
    let buyingNow = false;

    function getCartPayload() {
        const selectedSizeBtn = document.querySelector(".size-btn.active");
        const selectedColorBtn = document.querySelector(".color-dot.active");
        const selectedEngravingSideBtn = document.querySelector(".engraving-side-btn.active");
        const selectedDirectionBtn = document.querySelector(".name-direction-btn.active");
        const selectedFontBtn = document.querySelector(".name-font-btn.active");

        return {
            product_id: addCartBtn.dataset.productId,
            quantity: 1,
            size: selectedSizeBtn?.dataset.sizeName || "900ML",
            color: selectedColorBtn?.dataset.colorName || "",
            image: selectedColorBtn?.dataset.image || "",
            custom_name: document.getElementById("customName")?.value.trim() || "",
            engraving_side: selectedEngravingSideBtn?.dataset.engravingSide || "",
            name_direction: selectedDirectionBtn?.dataset.direction || "",
            name_font: selectedFontBtn?.dataset.font || ""
        };
    }

    async function addProductToCart() {
        const response = await fetch("/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: JSON.stringify(getCartPayload())
        });

        return await response.json();
    }

    addCartBtn.addEventListener("click", async function () {
        if (addingToCart) return;

        addingToCart = true;

        const originalText = addCartBtn.innerText;

        addCartBtn.disabled = true;
        addCartBtn.innerText = "Adicionando...";

        try {
            const data = await addProductToCart();

            if (data.success) {
                addCartBtn.innerText = "Adicionado";

                if (typeof openCart === "function") {
                    openCart();
                }

                setTimeout(() => {
                    addCartBtn.innerText = originalText;
                    addCartBtn.disabled = false;
                    addingToCart = false;
                }, 700);
            } else {
                addCartBtn.innerText = "Erro ao adicionar";

                setTimeout(() => {
                    addCartBtn.innerText = originalText;
                    addCartBtn.disabled = false;
                    addingToCart = false;
                }, 1200);
            }

        } catch (error) {
            console.error(error);

            addCartBtn.innerText = "Erro ao adicionar";

            setTimeout(() => {
                addCartBtn.innerText = originalText;
                addCartBtn.disabled = false;
                addingToCart = false;
            }, 1200);
        }
    });

    if (buyNowBtn) {
        buyNowBtn.addEventListener("click", async function (e) {
            e.preventDefault();

            if (buyingNow) return;

            buyingNow = true;

            const originalText = buyNowBtn.innerText;

            buyNowBtn.style.pointerEvents = "none";
            buyNowBtn.innerText = "Carregando...";

            try {
                const data = await addProductToCart();

                if (data.success) {
                    window.location.href = "{% url 'cart:checkout_page' %}";
                    return;
                }

                alert("Erro ao adicionar produto.");

            } catch (error) {
                console.error(error);
                alert("Erro ao adicionar produto.");
            }

            buyNowBtn.style.pointerEvents = "";
            buyNowBtn.innerText = originalText;
            buyingNow = false;
        });
    }
});
</script>

<script>
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (!target) return;

            e.preventDefault();

            const header = document.querySelector("header");
            const headerHeight = header ? header.offsetHeight : 0;
            const extraSpace = 30;

            const startPosition = window.pageYOffset;

            const targetPosition =
                target.getBoundingClientRect().top +
                window.pageYOffset -
                headerHeight -
                extraSpace;

            const distance = targetPosition - startPosition;
            const duration = 900;

            let startTime = null;

            function easeInOutCubic(t) {
                return t < 0.5
                    ? 4 * t * t * t
                    : 1 - Math.pow(-2 * t + 2, 3) / 2;
            }

            function animateScroll(currentTime) {
                if (startTime === null) {
                    startTime = currentTime;
                }

                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = easeInOutCubic(progress);

                window.scrollTo(0, startPosition + distance * ease);

                if (elapsed < duration) {
                    requestAnimationFrame(animateScroll);
                }
            }

            requestAnimationFrame(animateScroll);
        });
    });

    const cards = [...document.querySelectorAll(".community-card")];
    const numbersContainer = document.querySelector(".community-page-numbers");
    const prevBtn = document.querySelector(".community-page-btn.prev");
    const nextBtn = document.querySelector(".community-page-btn.next");

    if (cards.length && numbersContainer) {
        const perPage = 3;
        const totalPages = Math.ceil(cards.length / perPage);
        let currentPage = 1;

        function renderPage(page) {
            currentPage = page;

            cards.forEach((card, index) => {
                const start = (page - 1) * perPage;
                const end = start + perPage;

                card.style.display = index >= start && index < end ? "grid" : "none";
            });

            document
                .querySelectorAll(".community-page-number")
                .forEach(btn => btn.classList.remove("active"));

            const activeBtn = document.querySelector(`.community-page-number[data-page="${page}"]`);

            if (activeBtn) {
                activeBtn.classList.add("active");
            }

            if (prevBtn) {
                prevBtn.disabled = currentPage === 1;
            }

            if (nextBtn) {
                nextBtn.disabled = currentPage === totalPages;
            }
        }

        numbersContainer.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");

            btn.type = "button";
            btn.className = "community-page-number";
            btn.dataset.page = i;
            btn.textContent = i;

            btn.addEventListener("click", () => renderPage(i));

            numbersContainer.appendChild(btn);
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (currentPage > 1) {
                    renderPage(currentPage - 1);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                if (currentPage < totalPages) {
                    renderPage(currentPage + 1);
                }
            });
        }

        renderPage(1);
    }
});