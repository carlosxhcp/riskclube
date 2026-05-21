// =============================
// ELEMENTOS DO CARRINHO
// =============================

const openCartBtn = document.getElementById("openCartBtn");
const closeCartBtn = document.getElementById("closeCartBtn");
const sideCart = document.getElementById("sideCart");
const cartOverlay = document.getElementById("cartOverlay");
const sideCartContent = document.getElementById("sideCartContent");
const sideCartFooter = document.getElementById("sideCartFooter");
const freeShippingText = document.getElementById("freeShippingText");
const freeShippingProgress = document.getElementById("freeShippingProgress");
const cartCountBadge = document.getElementById("cartCountBadge");

// =============================
// ESTADO DO CARRINHO
// =============================

let shippingOptions = [];
let cartBusy = false;

// =============================
// FORMATAR DINHEIRO
// =============================

function formatMoney(value) {
    return "R$ " + Number(value || 0).toFixed(2).replace(".", ",");
}

// =============================
// CONTADOR DO CARRINHO
// =============================

function updateCartCount(data) {
    if (!cartCountBadge) return;

    let totalItems = 0;

    if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
            totalItems += Number(item.quantity || 0);
        });
    }

    cartCountBadge.innerText = totalItems;
    cartCountBadge.style.display = totalItems > 0 ? "flex" : "none";
}

// =============================
// PEGAR PREÇO DO FRETE
// =============================

function getShippingPrice(data) {
    if (!data) return 0;

    if (data.shipping_price !== undefined && data.shipping_price !== null) {
        return Number(data.shipping_price || 0);
    }

    if (data.shipping && data.shipping.price !== undefined) {
        return Number(data.shipping.price || 0);
    }

    return 0;
}

// =============================
// BLOQUEAR CARRINHO
// =============================

function setCartBusy(status) {
    cartBusy = status;

    document.querySelectorAll(".cart-qty-controls button").forEach(btn => {
        btn.disabled = status;
    });
}

// =============================
// ABRIR CARRINHO
// =============================

function openCart() {
    sideCart.classList.add("active");
    cartOverlay.classList.add("active");

    loadCart();
}

// =============================
// FECHAR CARRINHO
// =============================

function closeCart() {
    sideCart.classList.remove("active");
    cartOverlay.classList.remove("active");
}

// =============================
// BUSCAR CARRINHO
// =============================

async function loadCart() {
    const response = await fetch("/cart/data/");
    const data = await response.json();

    renderCart(data);
}

// =============================
// RENDERIZAR CARRINHO
// =============================

function renderCart(data) {

    updateCartCount(data);

    freeShippingProgress.style.width =
        data.free_shipping_progress + "%";

    if (data.free_shipping_remaining > 0) {
        freeShippingText.innerText =
            `Adicione mais ${formatMoney(data.free_shipping_remaining)} para Frete Grátis`;
    } else {
        freeShippingText.innerText =
            "Você ganhou Frete Grátis";
    }

    if (data.items.length === 0) {

        sideCartContent.innerHTML = `
            <div class="empty-cart-box">
                <i class="bi bi-cart-fill"></i>
                <p>Não há itens no carrinho</p>
            </div>
        `;

        sideCartFooter.innerHTML = "";

        return;
    }

    sideCartContent.innerHTML = data.items.map(item => `
        <div class="cart-item">

            <img src="${item.image}" alt="${item.name}">

            <div class="cart-item-info">

                <div class="cart-item-name">
                    ${item.name}
                </div>

                <div class="cart-item-size">
                    Cor: ${item.color || "-"}
                </div>

                <div class="cart-item-size">
                    Tamanho: ${item.size || "-"}
                </div>

                <div class="cart-item-installments">
                    ${item.installments}
                </div>

                <div class="cart-qty-controls">
                    <button type="button" onclick="updateCartQty('${item.cart_key}', -1)">−</button>

                    <span>${item.quantity}</span>

                    <button type="button" onclick="updateCartQty('${item.cart_key}', 1)">+</button>
                </div>

            </div>

            <div class="cart-item-price">
                ${formatMoney(item.subtotal)}
            </div>

        </div>
    `).join("");
}

// =============================
// ATUALIZAR QUANTIDADE
// =============================

async function updateCartQty(cartKey, change) {

    if (cartBusy) return;

    setCartBusy(true);

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

        alert("Erro ao atualizar carrinho.");

    } finally {

        setCartBusy(false);

    }
}

// =============================
// PEGAR CSRF TOKEN
// =============================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

// =============================
// EVENTOS
// =============================

if (openCartBtn) {
    openCartBtn.addEventListener("click", openCart);
}

if (closeCartBtn) {
    closeCartBtn.addEventListener("click", closeCart);
}

if (cartOverlay) {
    cartOverlay.addEventListener("click", closeCart);
}

// =============================
// CARREGAR CONTADOR
// =============================

fetch("/cart/data/")
    .then(response => response.json())
    .then(data => {
        updateCartCount(data);
    });