```js
const checkoutCepInput = document.getElementById("checkoutCepInput");
const checkoutShippingBtn = document.getElementById("checkoutShippingBtn");
const checkoutShippingOptions = document.getElementById("checkoutShippingOptions");

const checkoutCouponInput = document.getElementById("checkoutCouponInput");
const checkoutCouponBtn = document.getElementById("checkoutCouponBtn");
const checkoutCouponMessage = document.getElementById("checkoutCouponMessage");
const checkoutAppliedCoupons = document.getElementById("checkoutAppliedCoupons");

const paymentResult = document.getElementById("paymentResult");

const checkoutSubtotal = document.getElementById("checkoutSubtotal");
const checkoutDiscountRow = document.getElementById("checkoutDiscountRow");
const checkoutDiscount = document.getElementById("checkoutDiscount");
const checkoutShippingPrice = document.getElementById("checkoutShippingPrice");
const checkoutTotal = document.getElementById("checkoutTotal");

let currentCart = null;
let mpInstance = null;
let bricksBuilder = null;
let paymentBrickController = null;
let brickRendering = false;

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
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
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

function getMercadoPagoEmail(formData) {
    return String(formData?.payer?.email || "").trim().toLowerCase();
}

function validateBeforePayment(formData) {
    const email = getMercadoPagoEmail(formData);

    if (!email) {
        alert("Informe seu e-mail no campo do Mercado Pago.");
        return false;
    }

    if (!currentCart || !currentCart.items || !currentCart.items.length) {
        alert("Seu carrinho está vazio.");
        return false;
    }

    if (Number(currentCart.total || 0) <= 0) {
        alert("O total do pedido precisa ser maior que zero.");
        return false;
    }

    return true;
}

function updateSummary(data) {
    currentCart = data;

    if (checkoutSubtotal) {
        checkoutSubtotal.innerText = formatMoney(data.subtotal);
    }

    if (checkoutShippingPrice) {
        checkoutShippingPrice.innerText = formatMoney(data.shipping_price);
    }

    if (checkoutTotal) {
        checkoutTotal.innerText = formatMoney(data.total);
    }

    if (checkoutDiscountRow && checkoutDiscount) {
        if (Number(data.discount || 0) > 0) {
            checkoutDiscountRow.style.display = "flex";
            checkoutDiscount.innerText =
                "- " + formatMoney(data.discount);
        } else {
            checkoutDiscountRow.style.display = "none";
            checkoutDiscount.innerText = "- R$ 0,00";
        }
    }

    renderAppliedCoupons(data);
}

async function loadCheckoutCart() {
    try {
        const response = await fetch("/cart/data/");
        const data = await response.json();

        updateSummary(data);

        await renderPaymentBrick();

    } catch (error) {
        console.error(
            "Erro ao carregar carrinho:",
            error
        );
    }
}

function renderAppliedCoupons(data) {
    if (!checkoutAppliedCoupons) return;

    const coupons = Array.isArray(data.coupons)
        ? data.coupons
        : [];

    if (!coupons.length) {
        checkoutAppliedCoupons.innerHTML = "";
        return;
    }

    checkoutAppliedCoupons.innerHTML = coupons.map(coupon => `
        <div class="applied-coupon-item">
            <span>
                <strong>${escapeHtml(coupon.code)}</strong>
                •
                -${formatMoney(coupon.discount)}
            </span>

            <button
                type="button"
                class="remove-coupon-btn"
                data-coupon-code="${escapeHtml(coupon.code)}"
            >
                remover
            </button>
        </div>
    `).join("");
}

async function calculateShipping() {
    if (
        !checkoutCepInput ||
        !checkoutShippingBtn ||
        !checkoutShippingOptions
    ) {
        return;
    }

    const cep = normalizeCep(checkoutCepInput.value);

    if (cep.length !== 8) {
        setMessage(
            checkoutShippingOptions,
            "Digite um CEP válido."
        );
        return;
    }

    checkoutShippingBtn.disabled = true;
    checkoutShippingBtn.innerText = "Calculando...";

    setMessage(
        checkoutShippingOptions,
        "Calculando frete..."
    );

    try {
        const response = await fetch(
            "/cart/calculate-shipping/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ cep })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            setMessage(
                checkoutShippingOptions,
                data.error || "Erro ao calcular frete."
            );
            return;
        }

        checkoutShippingOptions.innerHTML =
            data.options.map((option, index) => `
                <label class="shipping-option">
                    <input
                        type="radio"
                        name="shipping_option"
                        data-id="${option.id}"
                        data-name="${option.name}"
                        data-company="${option.company || ""}"
                        data-price="${option.price}"
                        data-delivery-time="${option.delivery_time || ""}"
                        data-cep="${option.cep || cep}"
                        data-icon="${option.icon || ""}"
                        ${index === 0 ? "checked" : ""}
                    >

                    <span>
                        ${option.company || ""}
                        ${option.name}
                    </span>

                    <strong>
                        ${formatMoney(option.price)}
                    </strong>
                </label>
            `).join("");

        const firstOption =
            document.querySelector(
                'input[name="shipping_option"]:checked'
            );

        if (firstOption) {
            await selectShipping(firstOption);
        }

        document
            .querySelectorAll(
                'input[name="shipping_option"]'
            )
            .forEach(input => {
                input.addEventListener(
                    "change",
                    () => selectShipping(input)
                );
            });

    } catch (error) {
        console.error(
            "Erro ao calcular frete:",
            error
        );

        setMessage(
            checkoutShippingOptions,
            "Erro ao calcular frete."
        );

    } finally {
        checkoutShippingBtn.disabled = false;
        checkoutShippingBtn.innerText = "Calcular";
    }
}

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
        const response = await fetch(
            "/cart/select-shipping/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(
                data.error ||
                "Erro ao selecionar frete."
            );
            return;
        }

        updateSummary(data);

        await renderPaymentBrick();

    } catch (error) {
        console.error(
            "Erro ao selecionar frete:",
            error
        );

        alert("Erro ao selecionar frete.");
    }
}

async function applyCoupon() {
    const code =
        checkoutCouponInput.value.trim();

    if (!code) {
        setMessage(
            checkoutCouponMessage,
            "Digite um cupom."
        );
        return;
    }

    checkoutCouponBtn.disabled = true;
    checkoutCouponBtn.innerText = "Aplicando...";

    try {
        const response = await fetch(
            "/cart/apply-coupon/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ code })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            setMessage(
                checkoutCouponMessage,
                data.error || "Cupom inválido."
            );
            return;
        }

        checkoutCouponInput.value = "";

        setMessage(
            checkoutCouponMessage,
            "Cupom aplicado!"
        );

        updateSummary(data);

        await renderPaymentBrick();

    } catch (error) {
        console.error(
            "Erro ao aplicar cupom:",
            error
        );

        setMessage(
            checkoutCouponMessage,
            "Erro ao aplicar cupom."
        );

    } finally {
        checkoutCouponBtn.disabled = false;
        checkoutCouponBtn.innerText = "Aplicar";
    }
}

async function removeCoupon(code) {
    try {
        const response = await fetch(
            "/cart/remove-coupon/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ code })
            }
        );

        const data = await response.json();

        updateSummary(data);

        await renderPaymentBrick();

    } catch (error) {
        console.error(
            "Erro ao remover cupom:",
            error
        );
    }
}

async function renderPaymentBrick() {
    const container = document.getElementById("paymentBrick_container");

    if (!container || brickRendering) return;

    if (!window.MercadoPago || !window.MP_PUBLIC_KEY) {
        console.error("SDK do Mercado Pago ou MP_PUBLIC_KEY ausente.");
        return;
    }

    if (!currentCart || Number(currentCart.total || 0) <= 0) return;

    brickRendering = true;

    try {
        if (!mpInstance) {
            mpInstance = new MercadoPago(window.MP_PUBLIC_KEY, {
                locale: "pt-BR"
            });

            bricksBuilder = mpInstance.bricks();
        }

        if (
            paymentBrickController &&
            typeof paymentBrickController.unmount === "function"
        ) {
            await paymentBrickController.unmount();
            paymentBrickController = null;
        }

        container.innerHTML = "";

        if (paymentResult) {
            paymentResult.innerHTML = "";
        }

        paymentBrickController = await bricksBuilder.create(
            "payment",
            "paymentBrick_container",
            {
                initialization: {
                    amount: Number(currentCart.total || 0)
                },

                customization: {
                    visual: {
                        style: {
                            theme: "bootstrap"
                        }
                    },
                    paymentMethods: {
                        creditCard: "all",
                        debitCard: "all",
                        bankTransfer: "all",
                        ticket: "all",
                        maxInstallments: 6
                    }
                },

                callbacks: {
                    onReady: () => {
                        console.log("Payment Brick carregado.");
                    },

                    onSubmit: ({ selectedPaymentMethod, formData }) => {
                        return new Promise(async (resolve, reject) => {
                            if (!validateBeforePayment(formData)) {
                                reject();
                                return;
                            }

                            try {
                                const mpEmail = getMercadoPagoEmail(formData);

                                const payload = {
                                    email: mpEmail,
                                    selected_payment_method: selectedPaymentMethod,
                                    form_data: {
                                        ...formData,
                                        payer: {
                                            ...(formData.payer || {}),
                                            email: mpEmail
                                        }
                                    }
                                };

                                const response = await fetch(
                                    "/cart/checkout/mercadopago/",
                                    {
                                        method: "POST",
                                        headers: {
                                            "Content-Type": "application/json",
                                            "X-CSRFToken": getCookie("csrftoken")
                                        },
                                        body: JSON.stringify(payload)
                                    }
                                );

                                const data = await response.json();

                                if (!response.ok || !data.success) {
                                    console.log("ERRO MERCADO PAGO:", data);

                                    const details = data.details
                                        ? JSON.stringify(data.details)
                                        : "";

                                    alert(
                                        data.error ||
                                        details ||
                                        "Erro ao criar pagamento."
                                    );

                                    reject();
                                    return;
                                }

                                if (data.status === "approved") {
                                    window.location.href =
                                        `/sucesso/?order=${data.order_id}`;

                                    resolve();
                                    return;
                                }

                                if (
                                    data.pix_qr_code ||
                                    data.pix_qr_code_base64
                                ) {
                                    paymentResult.innerHTML = `
                                        <h3>Pix gerado com sucesso</h3>

                                        ${data.pix_qr_code_base64 ? `
                                            <img
                                                src="data:image/png;base64,${data.pix_qr_code_base64}"
                                                alt="QR Code Pix"
                                            >
                                        ` : ""}

                                        ${data.pix_qr_code ? `
                                            <label>Código Pix copia e cola</label>
                                            <textarea readonly>${escapeHtml(data.pix_qr_code)}</textarea>
                                            <button
                                                type="button"
                                                class="pay-btn"
                                                id="copyPixBtn"
                                            >
                                                Copiar código Pix
                                            </button>
                                        ` : ""}

                                        <p>Depois do pagamento, seu pedido será confirmado automaticamente.</p>
                                    `;

                                    const copyPixBtn =
                                        document.getElementById("copyPixBtn");

                                    if (copyPixBtn && data.pix_qr_code) {
                                        copyPixBtn.addEventListener(
                                            "click",
                                            async () => {
                                                await navigator.clipboard.writeText(
                                                    data.pix_qr_code
                                                );

                                                copyPixBtn.innerText =
                                                    "Código copiado!";
                                            }
                                        );
                                    }

                                    resolve();
                                    return;
                                }

                                alert(
                                    "Pagamento enviado. Status: " +
                                    (data.status || "pendente")
                                );

                                resolve();

                            } catch (error) {
                                console.error(
                                    "Erro ao enviar pagamento:",
                                    error
                                );

                                alert("Erro ao enviar pagamento.");
                                reject();
                            }
                        });
                    },

                    onError: (error) => {
                        console.error(
                            "Erro no Payment Brick:",
                            error
                        );
                    }
                }
            }
        );

    } catch (error) {
        console.error(
            "Erro ao carregar Payment Brick:",
            error
        );

        alert("Erro ao carregar pagamento.");

    } finally {
        brickRendering = false;
    }
}

if (checkoutShippingBtn) {
    checkoutShippingBtn.addEventListener(
        "click",
        calculateShipping
    );
}

if (checkoutCepInput) {
    checkoutCepInput.addEventListener("input", () => {
        const cep = normalizeCep(checkoutCepInput.value);

        if (cep.length > 5) {
            checkoutCepInput.value =
                cep.replace(/^(\d{5})(\d{0,3}).*/, "$1-$2");
        } else {
            checkoutCepInput.value = cep;
        }
    });

    checkoutCepInput.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            calculateShipping();
        }
    });
}

if (checkoutCouponBtn) {
    checkoutCouponBtn.addEventListener(
        "click",
        applyCoupon
    );
}

if (checkoutCouponInput) {
    checkoutCouponInput.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            applyCoupon();
        }
    });
}

document.addEventListener("click", event => {
    const removeCouponBtn =
        event.target.closest(".remove-coupon-btn");

    if (!removeCouponBtn) return;

    removeCoupon(removeCouponBtn.dataset.couponCode);
});

(async function initCheckout() {
    await loadCheckoutCart();
})();
```
