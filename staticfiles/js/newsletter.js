document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("newsletterPopup");
    const closeBtn = document.getElementById("closeNewsletterPopup");
    const noBtn = document.getElementById("noNewsletterPopup");

    if (!popup) return;

    const today = new Date().toISOString().slice(0, 10);
    const lastSeen = localStorage.getItem("riskNewsletterLastSeen");

    function openPopup() {
        popup.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closePopup() {
        popup.classList.remove("active");
        document.body.style.overflow = "";
        localStorage.setItem("riskNewsletterLastSeen", today);
    }

    if (lastSeen !== today) {
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
});