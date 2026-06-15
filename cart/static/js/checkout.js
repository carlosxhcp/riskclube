const checkoutCepInput = document.getElementById("checkoutCepInput");
const checkoutShippingBtn = document.getElementById("checkoutShippingBtn");
const checkoutShippingOptions = document.getElementById("checkoutShippingOptions");

const checkoutCouponInput = document.getElementById("checkoutCouponInput");
const checkoutCouponBtn = document.getElementById("checkoutCouponBtn");
const checkoutCouponMessage = document.getElementById("checkoutCouponMessage");
const checkoutAppliedCoupons = document.getElementById("checkoutAppliedCoupons");

const checkoutEmail = document.getElementById("checkoutEmail");
const payPixBtn = document.getElementById("payPixBtn");
const pixResult = document.getElementById("pixResult");

const checkoutSubtotal = document.getElementById("checkoutSubtotal");
const checkoutDiscountRow = document.getElementById("checkoutDiscountRow");
const checkoutDiscount = document.getElementById("checkoutDiscount");
const checkoutShippingPrice = document.getElementById("checkoutShippingPrice");
const checkoutTotal = document.getElementById("checkoutTotal");

let currentCart = null;

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

function normalizeCep(value) {
    return String(value || "").replace(/\D/g, "");
}

function setMessage(element, message) {
    if (!element) return;
    element.innerHTML = `<p>${escapeHtml(message)}</p>`;
}

function updateSummary(data) {
    currentCart = data;

    if (checkoutSubtotal) checkoutSubtotal.innerText = formatMoney(data.subtotal);
    if (checkoutShippingPrice) checkoutShippingPrice.innerText = formatMoney(data.shipping_price);
    if (checkoutTotal) checkoutTotal.innerText = formatMoney(data.total);

    if (checkoutDiscountRow && checkoutDiscount) {
        if (Number(data.discount || 0) > 0) {
            checkoutDiscountRow.style.display = "flex";
            checkoutDiscount.innerText = "- " + formatMoney(data.discount);
        } else {
            checkoutDiscountRow.style.display = "none";
            checkoutDiscount.innerText = "- R$ 0,00";
        }
    }

    renderAppliedCoupons(data);
}

async function loadCheckoutCart() {
    const response = await fetch("/cart/data/");
    const data = await response.json();
    updateSummary(data);
}

function renderAppliedCoupons(data) {
    if (!checkoutAppliedCoupons) return;

    const coupons = Array.isArray(data.coupons) ? data.coupons : [];

    if (!coupons.length) {
        checkoutAppliedCoupons.innerHTML = "";
        return;
    }

    checkoutAppliedCoupons.innerHTML = coupons.map(coupon => `
        <div class="applied-coupon-item">
            <span><strong>${escapeHtml(coupon.code)}</strong> • -${formatMoney(coupon.discount)}</span>
            <button type="button" class="remove-coupon-btn" data-coupon-code="${escapeHtml(coupon.code)}">
                remover
            </button>
        </div>
    `).join("");
}

async function calculateShipping() {
    const cep = normalizeCep(checkoutCepInput.value);

    if (cep.length !== 8) {
        setMessage(checkoutShippingOptions, "Digite um CEP válido.");
        return;
    }

    checkoutShippingBtn.disabled = true;
    checkoutShippingBtn.innerText = "Calculando...";
    setMessage(checkoutShippingOptions, "Calculando frete...");

    try {
        const response = await fetch("/cart/calculate-shipping/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ cep })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            setMessage(checkoutShippingOptions, data.error || "Erro ao calcular frete.");
            return;
        }

        checkoutShippingOptions.innerHTML = data.options.map((option, index) => `
            <label class="shipping-option">
                <input
                    type="radio"
                    name="shipping_option"
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
                    <span>
                        ${option.company ? escapeHtml(option.company) + " - " : ""}${escapeHtml(option.name)}
                        ${option.delivery_time ? `<small>${escapeHtml(option.delivery_time)} dias úteis</small>` : ""}
                    </span>
                </div>

                <strong>${formatMoney(option.price)}</strong>
            </label>
        `).join("");

        const first = document.querySelector('input[name="shipping_option"]:checked');

        if (first) {
            await selectShipping(first);
        }

        document.querySelectorAll('input[name="shipping_option"]').forEach(input => {
            input.addEventListener("change", () => selectShipping(input));
        });
    } finally {
        checkoutShippingBtn.disabled = false;
        checkoutShippingBtn.innerText = "Calcular";
    }
}

async function selectShipping(input) {
    const payload = {
        id: input.dataset.id,
        name: input.dataset.name,
        company: input.dataset.company,
        price: input.dataset.price,
        delivery_time: input.dataset.deliveryTime,
        cep: input.dataset.cep,
        icon: input.dataset.icon
    };

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

    updateSummary(data);
}

async function applyCoupon() {
    const code = checkoutCouponInput.value.trim();

    if (!code) {
        setMessage(checkoutCouponMessage, "Digite um cupom.");
        return;
    }

    checkoutCouponBtn.disabled = true;
    checkoutCouponBtn.innerText = "Aplicando...";

    try {
        const response = await fetch("/cart/apply-coupon/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            setMessage(checkoutCouponMessage, data.error || "Cupom inválido.");
            return;
        }

        checkoutCouponInput.value = "";
        setMessage(checkoutCouponMessage, "Cupom aplicado!");
        updateSummary(data);
    } finally {
        checkoutCouponBtn.disabled = false;
        checkoutCouponBtn.innerText = "Aplicar";
    }
}

async function removeCoupon(code) {
    const response = await fetch("/cart/remove-coupon/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ code })
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Erro ao remover cupom.");
        return;
    }

    setMessage(checkoutCouponMessage, "Cupom removido.");
    updateSummary(data);
}

async function payWithPix() {
    const email = checkoutEmail.value.trim();

    if (!email) {
        alert("Informe seu e-mail.");
        checkoutEmail.focus();
        return;
    }

    payPixBtn.disabled = true;
    payPixBtn.innerText = "Gerando Pix...";

    try {
        const response = await fetch("/cart/checkout/mercadopago/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                payment_type: "pix",
                email
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.error || "Erro ao gerar Pix.");
            return;
        }

        pixResult.innerHTML = `
            <h3>Pix gerado com sucesso</h3>

            ${data.pix_qr_code_base64 ? `
                <img src="data:image/png;base64,${data.pix_qr_code_base64}" alt="QR Code Pix">
            ` : ""}

            ${data.pix_qr_code ? `
                <label>Código Pix copia e cola</label>
                <textarea readonly>${data.pix_qr_code}</textarea>
                <button type="button" class="pay-btn" id="copyPixBtn">Copiar código Pix</button>
            ` : ""}

            <p>Depois do pagamento, seu pedido será confirmado automaticamente.</p>
        `;

        const copyPixBtn = document.getElementById("copyPixBtn");

        if (copyPixBtn && data.pix_qr_code) {
            copyPixBtn.addEventListener("click", async () => {
                await navigator.clipboard.writeText(data.pix_qr_code);
                copyPixBtn.innerText = "Código copiado!";
            });
        }
    } finally {
        payPixBtn.disabled = false;
        payPixBtn.innerText = "Gerar Pix";
    }
}

function initPaymentTabs() {
    document.querySelectorAll(".payment-tab").forEach(button => {
        button.addEventListener("click", () => {
            const tab = button.dataset.paymentTab;

            document.querySelectorAll(".payment-tab").forEach(btn => btn.classList.remove("active"));
            document.querySelectorAll(".payment-panel").forEach(panel => panel.classList.remove("active"));

            button.classList.add("active");

            if (tab === "pix") {
                document.getElementById("pixPanel").classList.add("active");
            }

            if (tab === "card") {
                document.getElementById("cardPanel").classList.add("active");
            }
        });
    });
}

async function initCardBrick() {
    if (!window.MP_PUBLIC_KEY || !document.getElementById("cardPaymentBrick_container")) return;

    const mp = new MercadoPago(window.MP_PUBLIC_KEY);
    const bricksBuilder = mp.bricks();

    await bricksBuilder.create("cardPayment", "cardPaymentBrick_container", {
        initialization: {
            amount: Number(currentCart?.total || 0)
        },
        callbacks: {
            onSubmit: async (cardFormData) => {
                const email = checkoutEmail.value.trim();

                if (!email) {
                    alert("Informe seu e-mail.");
                    checkoutEmail.focus();
                    return;
                }

                const response = await fetch("/cart/checkout/mercadopago/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({
                        payment_type: "card",
                        email,
                        token: cardFormData.token,
                        payment_method_id: cardFormData.payment_method_id,
                        issuer_id: cardFormData.issuer_id,
                        installments: cardFormData.installments,
                        identification_type: cardFormData.payer?.identification?.type,
                        identification_number: cardFormData.payer?.identification?.number
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(data.error || "Pagamento recusado.");
                    return;
                }

                if (data.status === "approved") {
                    window.location.href = `/sucesso/?order=${data.order_id}`;
                    return;
                }

                alert("Pagamento enviado. Status: " + data.status);
            },
            onError: (error) => {
                console.error(error);
                alert("Erro no formulário do cartão.");
            }
        }
    });
}

if (checkoutShippingBtn) {
    checkoutShippingBtn.addEventListener("click", calculateShipping);
}

if (checkoutCepInput) {
    checkoutCepInput.addEventListener("input", () => {
        const cep = normalizeCep(checkoutCepInput.value);

        if (cep.length > 5) {
            checkoutCepInput.value = cep.replace(/^(\d{5})(\d{0,3}).*/, "$1-$2");
        } else {
            checkoutCepInput.value = cep;
        }
    });
}

if (checkoutCouponBtn) {
    checkoutCouponBtn.addEventListener("click", applyCoupon);
}

if (payPixBtn) {
    payPixBtn.addEventListener("click", payWithPix);
}

document.addEventListener("click", event => {
    const removeCouponBtn = event.target.closest(".remove-coupon-btn");

    if (!removeCouponBtn) return;

    removeCoupon(removeCouponBtn.dataset.couponCode);
});

(async function initCheckout() {
    await loadCheckoutCart();
    initPaymentTabs();
    await initCardBrick();
})();