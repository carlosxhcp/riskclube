from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import DashboardProductForm, DashboardProductVariantForm, DashboardProductSizeForm, DashboardProductDefaultSizeForm
from products.models import Product, ProductVariant, ProductSize, ProductDefaultSize, VariantImage
from orders.models import Order
from django.contrib.auth.models import User


@staff_member_required
def dashboard_home(request):

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_customers = User.objects.count()

    latest_orders = Order.objects.order_by("-created_at")[:10]

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "latest_orders": latest_orders,
    }

    return render(
        request,
        "dashboard/home.html",
        context
    )

@staff_member_required
def products_list(request):
    products = Product.objects.all().order_by("-created")

    search = request.GET.get("q")

    if search:
        products = products.filter(name__icontains=search)

    context = {
        "products": products,
        "search": search,
    }

    return render(request, "dashboard/products_list.html", context)

@staff_member_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST" and request.POST.get("action") == "add_product_size":
        size_name = request.POST.get("size_name", "").strip()
        size_active = request.POST.get("size_active") == "on"

        if size_name:
            ProductDefaultSize.objects.create(
                product=product,
                name=size_name,
                active=size_active
            )

        return redirect("dashboard:product_edit", pk=product.pk)

    if request.method == "POST":
        form = DashboardProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard:products_list")
    else:
        form = DashboardProductForm(instance=product)

    return render(request, "dashboard/product_edit.html", {
        "form": form,
        "product": product,
    })

@staff_member_required
def variant_edit(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product = variant.product

    if request.method == "POST" and request.POST.get("action") == "add_variant_image":
        image = request.FILES.get("variant_image")
        alt = request.POST.get("alt", "").strip()

        if image:
            VariantImage.objects.create(
                variant=variant,
                image=image,
                alt=alt
            )

        return redirect("dashboard:variant_edit", pk=variant.pk)

    if request.method == "POST":
        form = DashboardProductVariantForm(
            request.POST,
            request.FILES,
            instance=variant
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard:product_edit", pk=product.pk)
    else:
        form = DashboardProductVariantForm(instance=variant)

    return render(request, "dashboard/variant_edit.html", {
        "form": form,
        "variant": variant,
        "product": product,
    })


@staff_member_required
def variant_create(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = DashboardProductVariantForm(request.POST, request.FILES)

        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            return redirect("dashboard:product_edit", pk=product.pk)
    else:
        form = DashboardProductVariantForm()

    return render(request, "dashboard/variant_edit.html", {
        "form": form,
        "variant": None,
        "product": product,
        "is_create": True,
    })

@staff_member_required
def size_create(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        form = DashboardProductSizeForm(request.POST)

        if form.is_valid():
            size = form.save(commit=False)
            size.variant = variant
            size.save()
            return redirect("dashboard:variant_edit", pk=variant.pk)
    else:
        form = DashboardProductSizeForm()

    return render(request, "dashboard/size_form.html", {
        "form": form,
        "variant": variant,
        "product": variant.product,
        "is_create": True,
    })


@staff_member_required
def size_edit(request, pk):
    size = get_object_or_404(ProductSize, pk=pk)
    variant = size.variant

    if request.method == "POST":
        form = DashboardProductSizeForm(request.POST, instance=size)

        if form.is_valid():
            form.save()
            return redirect("dashboard:variant_edit", pk=variant.pk)
    else:
        form = DashboardProductSizeForm(instance=size)

    return render(request, "dashboard/size_form.html", {
        "form": form,
        "size": size,
        "variant": variant,
        "product": variant.product,
        "is_create": False,
    })


@staff_member_required
def size_delete(request, pk):
    size = get_object_or_404(ProductSize, pk=pk)
    variant_pk = size.variant.pk
    size.delete()

    return redirect("dashboard:variant_edit", pk=variant_pk)


@staff_member_required
def product_size_create(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = DashboardProductDefaultSizeForm(request.POST)

        if form.is_valid():
            size = form.save(commit=False)
            size.product = product
            size.save()
            return redirect("dashboard:product_edit", pk=product.pk)
    else:
        form = DashboardProductDefaultSizeForm()

    return render(request, "dashboard/product_size_form.html", {
        "form": form,
        "product": product,
        "is_create": True,
    })


@staff_member_required
def product_size_edit(request, pk):
    size = get_object_or_404(ProductDefaultSize, pk=pk)
    product = size.product

    if request.method == "POST":
        form = DashboardProductDefaultSizeForm(request.POST, instance=size)

        if form.is_valid():
            form.save()
            return redirect("dashboard:product_edit", pk=product.pk)
    else:
        form = DashboardProductDefaultSizeForm(instance=size)

    return render(request, "dashboard/product_size_form.html", {
        "form": form,
        "size": size,
        "product": product,
        "is_create": False,
    })


@staff_member_required
def product_size_delete(request, pk):
    size = get_object_or_404(ProductDefaultSize, pk=pk)
    product_pk = size.product.pk
    size.delete()

    return redirect("dashboard:product_edit", pk=product_pk)


def variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product_id = variant.product.id

    variant.delete()

    return redirect("dashboard:product_edit", pk=product_id)


@staff_member_required
def variant_image_delete(request, pk):
    image = get_object_or_404(VariantImage, pk=pk)
    variant_pk = image.variant.pk

    image.delete()

    return redirect("dashboard:variant_edit", pk=variant_pk)