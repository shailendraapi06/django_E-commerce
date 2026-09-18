from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Product
from category.models import Category

from carts.models import CartItem



def store(request, category_slug=None):
    category = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug__iexact=category_slug,
            slug__iexact=product_slug,
            is_available=True,
        )
    except Product.DoesNotExist:
        raise Http404("Product not found")

    in_cart = False
    if request.session.session_key:
        in_cart = CartItem.objects.filter(
            cart__cart_id=request.session.session_key,
            product=single_product,
            is_active=True,
        ).exists()

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)