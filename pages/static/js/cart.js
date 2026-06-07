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

const shippingCepInput = document.getElementById("shippingCepInput");
const calculateShippingBtn = document.getElementById("calculateShippingBtn");
const shippingOptionsBox = document.getElementById("shippingOptions");
const cartShippingPrice = document.getElementById("cartShippingPrice");
const cartTotal = document.getElementById("cartTotal");
const cartSubtotal = document.getElementById("cartSubtotal");

// =============================
// ESTADO DO CARRINHO
// =============================

let selectedShippingPrice = 0;
let cartBusy = false;
let lastCartData = null;

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
// BLOQUEAR CARRINHO
// =============================

function setCartBusy(status) {
    cartBusy = status;

    document.querySelectorAll(".cart-qty-controls button").forEach(btn => {
        btn.disabled = status;
    });
}

// =============================
// ATUALIZAR TOTAIS
// =============================

function updateTotals(data) {
    if (!data) return;

    const subtotal = Number(data.subtotal || data.total || 0);
    const shipping = Number(selectedShippingPrice || 0);
    const total = subtotal + shipping;

    if (cartSubtotal) {
        cartSubtotal.innerText = formatMoney(subtotal);
    }

    if (cartShippingPrice) {
        cartShippingPrice.innerText = formatMoney(shipping);
    }

    if (cartTotal) {
        cartTotal.innerText = formatMoney(total);
    }
}

// =============================
// ABRIR CARRINHO
// =============================

function openCart() {
    if (!sideCart || !cartOverlay) return;

    sideCart.classList.add("active");
    cartOverlay.classList.add("active");

    loadCart();
}

// =============================
// FECHAR CARRINHO
// =============================

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
    lastCartData = data;

    updateCartCount(data);

    if (freeShippingProgress) {
        freeShippingProgress.style.width = `${data.free_shipping_progress || 0}%`;
    }

    if (freeShippingText) {
        if (data.free_shipping_remaining > 0) {
            freeShippingText.innerText =
                `Adicione mais ${formatMoney(data.free_shipping_remaining)} para Frete Grátis`;
        } else {
            freeShippingText.innerText = "Você ganhou Frete Grátis";
            selectedShippingPrice = 0;
        }
    }

    if (!data.items || data.items.length === 0) {
        selectedShippingPrice = 0;

        if (sideCartContent) {
            sideCartContent.innerHTML = `
                <div class="empty-cart-box">
                    <i class="bi bi-cart-fill"></i>
                    <p>Não há itens no carrinho</p>
                </div>
            `;
        }

        if (shippingOptionsBox) {
            shippingOptionsBox.innerHTML = "";
        }

        updateTotals(data);
        return;
    }

    if (sideCartContent) {
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
                        ${item.installments || ""}
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

    updateTotals(data);
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
        console.error("Erro ao atualizar carrinho:", error);
        alert("Erro ao atualizar carrinho.");
    } finally {
        setCartBusy(false);
    }
}

// =============================
// CALCULAR FRETE
// =============================

if (calculateShippingBtn) {
    calculateShippingBtn.addEventListener("click", () => {
        const cep = shippingCepInput.value.replace(/\D/g, "");

        if (cep.length !== 8) {
            shippingOptionsBox.innerHTML = "<p>Digite um CEP válido.</p>";
            return;
        }

        if (!lastCartData || !lastCartData.items || lastCartData.items.length === 0) {
            shippingOptionsBox.innerHTML = "<p>Adicione um produto ao carrinho antes de calcular o frete.</p>";
            return;
        }

        shippingOptionsBox.innerHTML = "<p>Calculando frete...</p>";

        setTimeout(() => {
            if (lastCartData.free_shipping_remaining <= 0) {
                selectedShippingPrice = 0;
            } else {
                selectedShippingPrice = 19.90;
            }

            shippingOptionsBox.innerHTML = `
                <label class="shipping-option">
                    <input type="radio" name="shipping" checked>
                    <span>Entrega padrão</span>
                    <strong>${formatMoney(selectedShippingPrice)}</strong>
                </label>
            `;

            updateTotals(lastCartData);
        }, 300);
    });
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

loadCart();