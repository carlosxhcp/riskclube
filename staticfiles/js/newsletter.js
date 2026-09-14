document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("newsletterPopup");
    const closeBtn = document.getElementById("closeNewsletterPopup");
    const noBtn = document.getElementById("noNewsletterPopup");

    const form = document.querySelector(".newsletter-form");
    const footerForm = document.querySelector(".footer-newsletter-form");

    // ==========================================
    // MINI POPUP DE MENSAGEM
    // ==========================================

    function showMiniPopup(message, type = "success") {
        const oldPopup = document.querySelector(".newsletter-mini-message");

        if (oldPopup) {
            oldPopup.remove();
        }

        const miniPopup = document.createElement("div");
        miniPopup.className = `newsletter-mini-message ${type}`;
        miniPopup.innerText = message;

        document.body.appendChild(miniPopup);

        setTimeout(() => {
            miniPopup.classList.add("show");
        }, 50);

        setTimeout(() => {
            miniPopup.classList.remove("show");

            setTimeout(() => {
                miniPopup.remove();
            }, 300);
        }, 3200);
    }


    // ==========================================
    // NEWSLETTER POPUP
    // ==========================================

    if (popup) {

        const popupClosed = sessionStorage.getItem("riskNewsletterClosed");

        function openPopup() {
            popup.classList.add("active");
            document.body.style.overflow = "hidden";
        }

        function closePopup() {
            popup.classList.remove("active");
            document.body.style.overflow = "";
            sessionStorage.setItem("riskNewsletterClosed", "true");
        }

        if (!popupClosed) {
            setTimeout(openPopup, 1200);
        }

        closeBtn?.addEventListener("click", closePopup);
        noBtn?.addEventListener("click", closePopup);

        popup.addEventListener("click", function (e) {
            if (e.target === popup) {
                closePopup();
            }
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && popup.classList.contains("active")) {
                closePopup();
            }
        });


        // ==========================================
        // ENVIO DA NEWSLETTER DO POPUP
        // ==========================================

        if (form) {

            form.addEventListener("submit", async function (e) {
                e.preventDefault();

                const button = form.querySelector("button");
                const originalText = button.innerText;

                button.disabled = true;
                button.innerText = "";

                try {
                    const formData = new FormData(form);

                    const response = await fetch(form.action, {
                        method: "POST",
                        body: formData,
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });

                    const data = await response.json();

                    if (data.success) {

                        closePopup();

                        showMiniPopup(
                            data.message || "Cupom enviado para seu e-mail!",
                            "success"
                        );

                        form.reset();

                    } else {

                        showMiniPopup(
                            data.message || "Não foi possível enviar o cupom.",
                            "error"
                        );
                    }

                } catch (error) {

                    console.error(error);

                    showMiniPopup(
                        "Erro ao enviar. Tente novamente.",
                        "error"
                    );

                } finally {

                    button.disabled = false;
                    button.innerText = originalText;
                }
            });
        }
    }


    // ==========================================
    // NEWSLETTER DO FOOTER
    // ==========================================

    if (footerForm) {

        footerForm.addEventListener("submit", async function (e) {

            e.preventDefault();

            const button = footerForm.querySelector("button");
            const input = footerForm.querySelector('input[name="email"]');

            const originalHTML = button.innerHTML;

            button.disabled = true;
            button.innerHTML = "";

            try {

                const formData = new FormData(footerForm);

                const response = await fetch(footerForm.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                if (data.success) {

                    showMiniPopup(
                        data.message || "Cupom enviado para seu e-mail!",
                        "success"
                    );

                    footerForm.reset();

                } else {

                    showMiniPopup(
                        data.message || "Não foi possível cadastrar o e-mail.",
                        "error"
                    );
                }

            } catch (error) {

                console.error(error);

                showMiniPopup(
                    "Erro ao enviar. Tente novamente.",
                    "error"
                );

            } finally {

                button.disabled = false;
                button.innerHTML = originalHTML;
            }
        });
    }

});