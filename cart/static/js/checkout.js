const checkoutCepInput = document.getElementById("checkoutCepInput");
const checkoutShippingBtn = document.getElementById("checkoutShippingBtn");
const checkoutShippingOptions = document.getElementById("checkoutShippingOptions");
const shippingTitle = document.getElementById("shippingTitle");


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

const checkoutCustomerName = document.getElementById("checkoutCustomerName");
const checkoutPhone = document.getElementById("checkoutPhone");
const checkoutAddressBox = document.getElementById("checkoutAddressBox");
const checkoutStreet = document.getElementById("checkoutStreet");
const checkoutNumber = document.getElementById("checkoutNumber");
const checkoutComplement = document.getElementById("checkoutComplement");
const checkoutNeighborhood = document.getElementById("checkoutNeighborhood");
const checkoutCity = document.getElementById("checkoutCity");
const checkoutState = document.getElementById("checkoutState");

let currentCart = null;
let mpInstance = null;
let bricksBuilder = null;
let paymentBrickController = null;
let brickRendering = false;

function renderAutomaticFreeShipping() {
    if (!checkoutShippingOptions) return;

    setShippingTitle("Opções de frete");

    checkoutShippingOptions.innerHTML = `
        <label class="shipping-option">
            <input
                type="radio"
                name="shipping_option"
                data-id="free_shipping"
                data-name="Frete grátis"
                data-company="Risk Clube"
                data-price="0"
                data-delivery-time=""
                data-cep=""
                data-icon=""
                checked
            >

            <div class="shipping-company">
                <img
                    src="/static/img/shipping/truck.png"
                    class="shipping-logo"
                    alt=""
                >

                <span>Frete grátis</span>
            </div>

            <strong>R$ 0,00</strong>
        </label>

        ${renderDisabledShippingOptions()}
    `;
}

function getShippingLogo(companyName) {
    const name = (companyName || "").toLowerCase();

    if (name.includes("loggi")) {
        return "/static/img/shipping/loggi.png";
    }

    if (
        name.includes("correios") ||
        name.includes("sedex") ||
        name.includes("pac")
    ) {
        return "/static/img/shipping/correios.png";
    }

    if (name.includes("jadlog")) {
        return "/static/img/shipping/jadlog.png";
    }

    return "/static/img/shipping/truck.png";
}

function renderDisabledShippingOptions() {
    return `
        <div class="shipping-placeholder-options shipping-disabled-options">
            <div class="shipping-placeholder-card">
                <span>Loggi Express</span>
                <small>Indisponível para este pedido</small>
            </div>

            <div class="shipping-placeholder-card">
                <span>Correios Sedex</span>
                <small>Indisponível para este pedido</small>
            </div>

            <div class="shipping-placeholder-card">
                <span>Jadlog Package</span>
                <small>Indisponível para este pedido</small>
            </div>
        </div>
    `;
}

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

function clearShippingOptions() {
    if (checkoutShippingOptions) {
        checkoutShippingOptions.innerHTML = "";
    }
}

function setShippingPlaceholder(message = "Informe seu CEP para calcular o frete") {
    if (!shippingTitle) return;

    shippingTitle.innerText = message;
    shippingTitle.classList.add("shipping-placeholder");
}

function setShippingTitle(message = "Opções de frete") {
    if (!shippingTitle) return;

    shippingTitle.innerText = message;
    shippingTitle.classList.remove("shipping-placeholder");
}

function clearAddressFields() {
    if (checkoutStreet) checkoutStreet.value = "";
    if (checkoutNumber) checkoutNumber.value = "";
    if (checkoutComplement) checkoutComplement.value = "";
    if (checkoutNeighborhood) checkoutNeighborhood.value = "";
    if (checkoutCity) checkoutCity.value = "";
    if (checkoutState) checkoutState.value = "";
}

async function fillAddressByCep(cep) {
    if (cep.length !== 8) return false;

    try {
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await response.json();

        if (data.erro) {
            clearAddressFields();

            if (checkoutAddressBox) {
                checkoutAddressBox.style.display = "none";
            }

            alert("CEP não encontrado.");
            return false;
        }

        if (checkoutAddressBox) {
            checkoutAddressBox.style.display = "grid";
        }

        if (checkoutStreet) checkoutStreet.value = data.logradouro || "";
        if (checkoutNeighborhood) checkoutNeighborhood.value = data.bairro || "";
        if (checkoutCity) checkoutCity.value = data.localidade || "";
        if (checkoutState) checkoutState.value = data.uf || "";

        if (checkoutNumber) checkoutNumber.focus();

        return true;

    } catch (error) {
        console.error("Erro ao buscar endereço:", error);
        alert("Não foi possível buscar o endereço pelo CEP.");
        return false;
    }
}

function getCheckoutEmail(formData) {
    return String(formData?.payer?.email || "").trim().toLowerCase();
}

function validateBeforePayment(formData) {
    const email = getCheckoutEmail(formData);

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
    if (!checkoutCustomerName?.value.trim()) {
        alert("Informe seu nome completo.");
        return false;
    }

    if (!checkoutPhone?.value.trim()) {
        alert("Informe seu telefone.");
        return false;
    }

    if (!normalizeCep(checkoutCepInput?.value).length) {
        alert("Informe seu CEP.");
        return false;
    }

    if (!checkoutStreet?.value.trim()) {
        alert("Informe sua rua.");
        return false;
    }

    if (!checkoutNumber?.value.trim()) {
        alert("Informe o número do endereço.");
        return false;
    }

    if (!checkoutNeighborhood?.value.trim()) {
        alert("Informe seu bairro.");
        return false;
    }

    if (!checkoutCity?.value.trim()) {
        alert("Informe sua cidade.");
        return false;
    }

    if (!checkoutState?.value.trim()) {
        alert("Informe seu estado.");
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
            checkoutDiscount.innerText = "- " + formatMoney(data.discount);
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

        if (Number(data.subtotal || 0) >= 249) {
            const freeCart = {
                ...data,
                shipping_price: 0,
                total: Number(data.subtotal || 0) - Number(data.discount || 0)
            };

            updateSummary(freeCart);
            renderAutomaticFreeShipping();
        } else {
            setShippingPlaceholder();
        }

        await renderPaymentBrick();

    } catch (error) {
        console.error("Erro ao carregar carrinho:", error);
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
        setShippingPlaceholder();
        setMessage(
            checkoutShippingOptions,
            "Digite um CEP válido."
        );
        return;
    }

    checkoutShippingBtn.disabled = true;
    checkoutShippingBtn.innerText = "Calculando...";

    setShippingPlaceholder("Calculando frete...");
    clearShippingOptions();

    try {
        const addressFound = await fillAddressByCep(cep);

        if (!addressFound) {
            setShippingPlaceholder();
            clearShippingOptions();
            return;
        }

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
            setShippingPlaceholder();
            setMessage(
                checkoutShippingOptions,
                data.error || "Erro ao calcular frete."
            );
            return;
        }

        if (!Array.isArray(data.options) || !data.options.length) {
            setShippingPlaceholder("Nenhuma opção de frete encontrada.");
            clearShippingOptions();
            return;
        }

        setShippingTitle();

        const onlyFreeShipping =
            data.options.length === 1 &&
            Number(data.options[0].price || 0) === 0;
        checkoutShippingOptions.innerHTML =
            data.options.map((option, index) => `
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

                    <div class="shipping-company">
                        <img
                            src="${getShippingLogo(option.company)}"
                            class="shipping-logo"
                            alt=""
                        >

                        <span>
                            ${escapeHtml(option.company || "")}
                            ${escapeHtml(option.name)}
                        </span>
                    </div>

                    <strong>
                        ${formatMoney(option.price)}
                    </strong>
                </label>
            `).join("") + (onlyFreeShipping ? renderDisabledShippingOptions() : "");

        const firstOption =
            document.querySelector(
                'input[name="shipping_option"]:checked'
            );

        if (firstOption) {
            await selectShipping(firstOption);
        }

        document
            .querySelectorAll('input[name="shipping_option"]')
            .forEach(input => {
                input.addEventListener(
                    "change",
                    () => selectShipping(input)
                );
            });

    } catch (error) {
        console.error("Erro ao calcular frete:", error);

        setShippingPlaceholder();
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
        console.error("Erro ao selecionar frete:", error);
        alert("Erro ao selecionar frete.");
    }
}

async function applyCoupon() {
    const code = checkoutCouponInput.value.trim();

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
        console.error("Erro ao aplicar cupom:", error);

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
        console.error("Erro ao remover cupom:", error);
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
                                const payload = {
                                    email: getCheckoutEmail(formData),
                                    selected_payment_method: selectedPaymentMethod,
                                    address: {
                                        customer_name: checkoutCustomerName?.value || "",
                                        phone: checkoutPhone?.value || "",
                                        cep: normalizeCep(checkoutCepInput.value),
                                        street: checkoutStreet?.value || "",
                                        number: checkoutNumber?.value || "",
                                        complement: checkoutComplement?.value || "",
                                        neighborhood: checkoutNeighborhood?.value || "",
                                        city: checkoutCity?.value || "",
                                        state: checkoutState?.value || ""
                                    },
                                    form_data: {
                                        ...formData,
                                        payer: {
                                            ...(formData.payer || {}),
                                            email: getCheckoutEmail(formData)
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
                                        `/pedido/${data.order_id}/sucesso/`;

                                    resolve();
                                    return;
                                }

                                if (
                                    data.pix_qr_code ||
                                    data.pix_qr_code_base64
                                ) {
                                    sessionStorage.setItem(
                                        `pix_order_${data.order_id}`,
                                        JSON.stringify({
                                            qr_code: data.pix_qr_code,
                                            qr_code_base64: data.pix_qr_code_base64
                                        })
                                    );

                                    window.location.href =
                                        `/pedido/${data.order_id}/pix/`;

                                    resolve();
                                    return;
                                } <p>Depois do pagamento, seu pedido será confirmado automaticamente.</p>
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
                                console.error("Erro ao enviar pagamento:", error);

                                alert("Erro ao enviar pagamento.");
                                reject();
                            }
                        });
                    },

                    onError: (error) => {
                        console.error("Erro no Payment Brick:", error);
                    }
                }
            }
        );

    } catch (error) {
        console.error("Erro ao carregar Payment Brick:", error);
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

        if (cep.length < 8) {
            if (currentCart && Number(currentCart.subtotal || 0) >= 249) {
                renderAutomaticFreeShipping();
            } else {
                setShippingPlaceholder();
                clearShippingOptions();
            }
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
    setShippingPlaceholder();
    await loadCheckoutCart();
})();