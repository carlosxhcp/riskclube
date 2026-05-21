// =============================
// MENU MOBILE
// =============================

const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const closeMobileMenu = document.getElementById("closeMobileMenu");
const mobileMenu = document.getElementById("mobileMenu");
const mobileOverlay = document.getElementById("mobileOverlay");

function openMobileMenu() {
    mobileMenu.classList.add("active");
    mobileOverlay.classList.add("active");
}

function closeMenu() {
    mobileMenu.classList.remove("active");
    mobileOverlay.classList.remove("active");
}

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", openMobileMenu);
}

if (closeMobileMenu) {
    closeMobileMenu.addEventListener("click", closeMenu);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener("click", closeMenu);
}