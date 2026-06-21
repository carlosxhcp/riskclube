from django import forms
from products.models import Product, ProductVariant, ProductSize, ProductDefaultSize


class DashboardProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "price",
            "image",
            "back_image",
            "image_hover",
            "description",
            "engraving_position",
            "default_color_name",
            "default_color_hex",
            "available",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }



class DashboardProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = [
            "color_name",
            "color_hex",
            "image",
            "image_hover",
            "back_image",
            "active",
        ]

class DashboardProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = [
            "name",
            "active",
        ]
class DashboardProductDefaultSizeForm(forms.ModelForm):
    class Meta:
        model = ProductDefaultSize
        fields = [
            "name",
            "active",
        ]