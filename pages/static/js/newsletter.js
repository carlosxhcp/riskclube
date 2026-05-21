// =============================
// ELEMENTOS NEWSLETTER
// =============================

const newsletterPopup = document.getElementById("newsletterPopup");
const closeNewsletterPopup = document.getElementById("closeNewsletterPopup");
const noNewsletterPopup = document.getElementById("noNewsletterPopup");

// =============================
// FECHAR NEWSLETTER
// =============================

function closeNewsletter() {
    if (!newsletterPopup) return;

    newsletterPopup.classList.remove("active");

    sessionStorage.setItem("newsletter_closed", "true");
}

// =============================
// ABRIR NEWSLETTER
// =============================

window.addEventListener("load", () => {
    if (!newsletterPopup) return;

    const popupClosed = sessionStorage.getItem("newsletter_closed");

    if (!popupClosed) {
        setTimeout(() => {
            newsletterPopup.classList.add("active");
        }, 1200);
    }
});

// =============================
// EVENTOS
// =============================

if (closeNewsletterPopup) {
    closeNewsletterPopup.addEventListener("click", closeNewsletter);
}

if (noNewsletterPopup) {
    noNewsletterPopup.addEventListener("click", closeNewsletter);
}

if (newsletterPopup) {
    newsletterPopup.addEventListener("click", (e) => {
        if (e.target === newsletterPopup) {
            closeNewsletter();
        }
    });
}