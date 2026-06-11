// =============================
// ELEMENTOS DO CARRINHO
// =============================

const openCartBtn = document.getElementById("openCartBtn");
const closeCartBtn = document.getElementById("closeCartBtn");
const sideCart = document.getElementById("sideCart");
const cartOverlay = document.getElementById("cartOverlay");
const sideCartContent = document.getElementById("sideCartContent");
const freeShippingText = document.getElementById("freeShippingText");
const freeShippingProgress = document.getElementById("freeShippingProgress");
const cartCountBadge = document.getElementById("cartCountBadge");

const shippingCepInput = document.getElementById("shippingCepInput");
const calculateShippingBtn = document.getElementById("calculateShippingBtn");
const shippingOptionsBox = document.getElementById("shippingOptions");

const cartSubtotal = document.getElementById("cartSubtotal");
const cartShippingPrice = document.getElementById("cartShippingPrice");
const cartTotal = document.getElementById("cartTotal");

// =============================
// ESTADO
// =============================

let cartBusy = false;
let lastCartData = null;

// =============================
// HELPERS
// =============================

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

function filterShippingOptions(options) {
    if (!Array.isArray(options)) return [];

    return options.filter(option => {
        const text = `${option.company || ""} ${option.name || ""}`.toLowerCase();

        const isJadlog = text.includes("jadlog");
        const isLoggiExpress = text.includes("loggi") && text.includes("express");
        const isCorreios = text.includes("correios") || text.includes("sedex") || text.includes("pac");

        return !isJadlog && (isLoggiExpress || isCorreios);
    });
}

// =============================
// CONTADOR
// =============================

function updateCartCount(data) {
    if (!cartCountBadge) return;

    let totalItems = 0;

    if (data.items) {
        data.items.forEach(item => {
            totalItems += Number(item.quantity || 0);
        });
    }

    cartCountBadge.innerText = totalItems;
    cartCountBadge.style.display = totalItems > 0 ? "flex" : "none";
}

// =============================
// TOTAIS
// =============================

function updateTotals(data) {
    if (!data) return;

    if (cartSubtotal) {
        cartSubtotal.innerText = formatMoney(data.subtotal || 0);
    }

    if (cartShippingPrice) {
        cartShippingPrice.innerText = formatMoney(data.shipping_price || 0);
    }

    if (cartTotal) {
        cartTotal.innerText = formatMoney(data.total || 0);
    }
}

// =============================
// ABRIR / FECHAR
// =============================

function openCart() {
    if (!sideCart || !cartOverlay) return;

    sideCart.classList.add("active");
    cartOverlay.classList.add("active");

    loadCart();
}

function closeCart() {
    if (!sideCart || !cartOverlay) return;

    sideCart.classList.remove("active");
    cartOverlay.classList.remove("active");
}

// =============================
// BUSCAR CARRINHO
// =============================

async function loadCart() {
    try {
        const response = await fetch("/cart/data/");
        const data = await response.json();

        renderCart(data);
    } catch (error) {
        console.error("Erro ao carregar carrinho:", error);
    }
}

// =============================
// RENDERIZAR CARRINHO
// =============================

function renderCart(data) {
    const previousHadShipping = lastCartData && lastCartData.shipping;
    const nowHasShipping = data && data.shipping;

    lastCartData = data;

    updateCartCount(data);
    updateTotals(data);

    if (shippingOptionsBox && !nowHasShipping) {
        if (data.items && data.items.length > 0 && previousHadShipping) {
            shippingOptionsBox.innerHTML = `<p>Calcule o frete novamente.</p>`;
        } else if (!data.items || data.items.length === 0) {
            shippingOptionsBox.innerHTML = "";
        }
    }

    if (freeShippingProgress) {
        freeShippingProgress.style.width = `${data.free_shipping_progress || 0}%`;
    }

    if (freeShippingText) {
        if (data.free_shipping_remaining > 0) {
            freeShippingText.innerText =
                `Adicione mais ${formatMoney(data.free_shipping_remaining)} para Frete Grátis`;
        } else {
            freeShippingText.innerText = "Você ganhou Frete Grátis";
        }
    }

    if (!sideCartContent) return;

    if (!data.items || data.items.length === 0) {
        sideCartContent.innerHTML = `
            <div class="empty-cart-box">
                <i class="bi bi-cart-fill"></i>
                <p>Não há itens no carrinho</p>
            </div>
        `;

        if (shippingOptionsBox) {
            shippingOptionsBox.innerHTML = "";
        }

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

                    <div class="cart-item-installments">
                        ${escapeHtml(item.installments || "")}
                    </div>

                    <div class="cart-qty-controls">
                        <button type="button" class="cart-qty-btn" data-cart-key="${escapeHtml(item.cart_key)}" data-change="-1">−</button>
                        <span>${item.quantity}</span>
                        <button type="button" class="cart-qty-btn" data-cart-key="${escapeHtml(item.cart_key)}" data-change="1">+</button>
                    </div>
                </div>

                <div class="cart-item-price">
                    ${formatMoney(item.subtotal)}
                </div>
            </div>
        `;
    }).join("");
}

// =============================
// ATUALIZAR QUANTIDADE
// =============================

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

// =============================
// CLIQUE NOS BOTÕES + E -
// =============================

document.addEventListener("click", function (event) {
    const button = event.target.closest(".cart-qty-btn");

    if (!button) return;

    const cartKey = button.dataset.cartKey;
    const change = Number(button.dataset.change);

    if (!cartKey || !change) return;

    updateCartQty(cartKey, change);
});

// =============================
// CALCULAR FRETE
// =============================

async function calculateShipping() {
    if (!shippingCepInput || !shippingOptionsBox) return;

    const cep = shippingCepInput.value.replace(/\D/g, "");

    if (cep.length !== 8) {
        shippingOptionsBox.innerHTML = `<p>Digite um CEP válido.</p>`;
        return;
    }

    if (!lastCartData || !lastCartData.items || lastCartData.items.length === 0) {
        shippingOptionsBox.innerHTML = `<p>Adicione um produto ao carrinho antes de calcular o frete.</p>`;
        return;
    }

    shippingOptionsBox.innerHTML = `<p>Calculando frete...</p>`;

    try {
        const response = await fetch("/cart/calculate-shipping/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                cep: cep
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            shippingOptionsBox.innerHTML = `<p>${data.error || "Erro ao calcular frete."}</p>`;
            return;
        }

        data.options = filterShippingOptions(data.options);

        if (!data.options || data.options.length === 0) {
            shippingOptionsBox.innerHTML = `<p>Nenhuma opção de frete disponível.</p>`;
            return;
        }

        shippingOptionsBox.innerHTML = data.options.map((option, index) => `
            <label class="shipping-option">
                <input
                    type="radio"
                    name="shipping_option"
                    value="${escapeHtml(option.id)}"
                    data-id="${escapeHtml(option.id)}"
                    data-name="${escapeHtml(option.name)}"
                    data-company="${escapeHtml(option.company || "")}"
                    data-price="${escapeHtml(option.price)}"
                    data-delivery-time="${escapeHtml(option.delivery_time || "")}"
                    data-cep="${escapeHtml(option.cep || cep)}"
                    data-icon="${escapeHtml(option.icon || "")}"
                    ${index === 0 ? "checked" : ""}
                >

                <div class="shipping-option-info">
                    ${
                        option.icon
                            ? `<img src="${escapeHtml(option.icon)}" class="shipping-company-icon" alt="${escapeHtml(option.company || option.name)}">`
                            : `<span class="shipping-company-fallback">🚚</span>`
                    }

                    <span>
                        ${option.company ? escapeHtml(option.company) + " - " : ""}${escapeHtml(option.name)}
                        ${option.delivery_time ? `<small>${escapeHtml(option.delivery_time)} dias úteis</small>` : ""}
                    </span>
                </div>

                <strong>${formatMoney(option.price)}</strong>
            </label>
        `).join("");

        const firstOption = document.querySelector('input[name="shipping_option"]:checked');

        if (firstOption) {
            await selectShipping(firstOption);
        }

        document.querySelectorAll('input[name="shipping_option"]').forEach(input => {
            input.addEventListener("change", async () => {
                await selectShipping(input);
            });
        });

    } catch (error) {
        console.error("Erro ao calcular frete:", error);
        shippingOptionsBox.innerHTML = `<p>Erro ao calcular frete.</p>`;
    }
}

// =============================
// SELECIONAR FRETE
// =============================

async function selectShipping(input) {
    if (!input) return;

    const payload = {
        id: input.dataset.id,
        name: input.dataset.name,
        company: input.dataset.company,
        price: input.dataset.price,
        delivery_time: input.dataset.deliveryTime,
        cep: input.dataset.cep,
        icon: input.dataset.icon
    };

    try {
        const response = await fetch("/cart/select-shipping/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.error || "Erro ao selecionar frete.");
            return;
        }

        renderCart(data);

    } catch (error) {
        console.error("Erro ao selecionar frete:", error);
        alert("Erro ao selecionar frete.");
    }
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

if (calculateShippingBtn) {
    calculateShippingBtn.addEventListener("click", calculateShipping);
}

if (shippingCepInput) {
    shippingCepInput.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            calculateShipping();
        }
    });
}

// =============================
// INICIAR
// =============================

loadCart();