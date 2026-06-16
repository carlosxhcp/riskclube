const openCartBtn = document.getElementById("openCartBtn");
const closeCartBtn = document.getElementById("closeCartBtn");
const sideCart = document.getElementById("sideCart");
const cartOverlay = document.getElementById("cartOverlay");
const sideCartContent = document.getElementById("sideCartContent");
const cartCountBadge = document.getElementById("cartCountBadge");

const cartSubtotal = document.getElementById("cartSubtotal");
const cartTotal = document.getElementById("cartTotal");

const freeShippingText = document.getElementById("freeShippingText");
const freeShippingProgress = document.getElementById("freeShippingProgress");

const FREE_SHIPPING_LIMIT = 249;

let cartBusy = false;

function formatMoney(value) {
    return "R$ " + Number(value || 0).toFixed(2).replace(".", ",");
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function escapeHtml(value) {
    return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function updateCartCount(data) {
    if (!cartCountBadge) return;

    let totalItems = 0;

    if (data && Array.isArray(data.items)) {
        data.items.forEach(item => {
            totalItems += Number(item.quantity || 0);
        });
    }

    cartCountBadge.innerText = totalItems;
    cartCountBadge.style.display = totalItems > 0 ? "flex" : "none";
}

function updateTotals(data) {
    if (!data) return;

    const subtotal = Number(data.subtotal || 0);

    if (cartSubtotal) {
        cartSubtotal.innerText = formatMoney(subtotal);
    }

    if (cartTotal) {
        cartTotal.innerText = formatMoney(subtotal);
    }
}

function updateFreeShipping(data) {
    if (!freeShippingText || !freeShippingProgress) return;

    const subtotal = Number(data?.subtotal || 0);
    const missing = Math.max(FREE_SHIPPING_LIMIT - subtotal, 0);
    const percent = Math.min((subtotal / FREE_SHIPPING_LIMIT) * 100, 100);

    freeShippingProgress.style.width = `${percent}%`;

    if (subtotal <= 0) {
        freeShippingText.innerText = "Adicione R$ 249,00 para ganhar frete grátis";
        return;
    }

    if (missing > 0) {
        freeShippingText.innerText = `Adicione mais ${formatMoney(missing)} para ganhar frete grátis`;
    } else {
        freeShippingText.innerText = "Você ganhou frete grátis!";
    }
}

function openCart() {
    if (!sideCart || !cartOverlay) return;

    sideCart.classList.add("active");
    cartOverlay.classList.add("active");
    document.body.classList.add("cart-locked");

    loadCart();
}

function closeCart() {
    if (!sideCart || !cartOverlay) return;

    sideCart.classList.remove("active");
    cartOverlay.classList.remove("active");
    document.body.classList.remove("cart-locked");
}

async function loadCart() {
    try {
        const response = await fetch("/cart/data/");
        const data = await response.json();

        renderCart(data);
    } catch (error) {
        console.error("Erro ao carregar carrinho:", error);
    }
}

function renderCart(data) {
    if (!data) return;

    updateCartCount(data);
    updateTotals(data);
    updateFreeShipping(data);

    if (!sideCartContent) return;

    if (!data.items || data.items.length === 0) {
        sideCartContent.innerHTML = `
            <div class="empty-cart-box">
                <i class="bi bi-bag"></i>
                <p>Não há itens no carrinho</p>
                <small>Adicione uma garrafa para continuar.</small>
            </div>
        `;

        return;
    }

    sideCartContent.innerHTML = data.items.map(item => {
        const customNameHtml = item.custom_name
            ? `<div class="cart-item-size">Nome: ${escapeHtml(item.custom_name)}</div>`
            : "";

        const engravingHtml = item.engraving_side
            ? `<div class="cart-item-size">Gravação: ${escapeHtml(item.engraving_side)}</div>`
            : "";

        const directionHtml = item.name_direction
            ? `<div class="cart-item-size">Direção: ${escapeHtml(item.name_direction)}</div>`
            : "";

        return `
            <div class="cart-item">
                <img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}">

                <div class="cart-item-info">
                    <div class="cart-item-name">
                        ${escapeHtml(item.name)}
                    </div>

                    <div class="cart-item-size">
                        Cor: ${escapeHtml(item.color || "-")}
                    </div>

                    <div class="cart-item-size">
                        Tamanho: ${escapeHtml(item.size || "-")}
                    </div>

                    ${customNameHtml}
                    ${engravingHtml}
                    ${directionHtml}

                    <div class="cart-qty-controls">
                        <button 
                            type="button" 
                            class="cart-qty-btn" 
                            data-cart-key="${escapeHtml(item.cart_key)}" 
                            data-change="-1"
                        >
                            −
                        </button>

                        <span>${Number(item.quantity || 0)}</span>

                        <button 
                            type="button" 
                            class="cart-qty-btn" 
                            data-cart-key="${escapeHtml(item.cart_key)}" 
                            data-change="1"
                        >
                            +
                        </button>
                    </div>
                </div>

                <div class="cart-item-price">
                    ${formatMoney(item.subtotal)}
                </div>
            </div>
        `;
    }).join("");
}

async function updateCartQty(cartKey, change) {
    if (cartBusy) return;

    cartBusy = true;

    try {
        const response = await fetch("/cart/update/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                cart_key: cartKey,
                change: change
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.error || "Erro ao atualizar carrinho.");
            return;
        }

        renderCart(data);
    } catch (error) {
        console.error("Erro ao atualizar carrinho:", error);
        alert("Erro ao atualizar carrinho.");
    } finally {
        cartBusy = false;
    }
}

if (openCartBtn) {
    openCartBtn.addEventListener("click", openCart);
}

if (closeCartBtn) {
    closeCartBtn.addEventListener("click", closeCart);
}

if (cartOverlay) {
    cartOverlay.addEventListener("click", closeCart);
}

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeCart();
    }
});

document.addEventListener("click", function (event) {
    const qtyButton = event.target.closest(".cart-qty-btn");

    if (!qtyButton) return;

    const cartKey = qtyButton.dataset.cartKey;
    const change = Number(qtyButton.dataset.change);

    if (!cartKey || !change) return;

    updateCartQty(cartKey, change);
});

loadCart();