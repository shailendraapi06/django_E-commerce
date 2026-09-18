from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Product
from category.models import Category

from carts.models import CartItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def store(request, category_slug=None):
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories,
            is_available=True,
        ).order_by('-created_date', '-id')
    else:
        products = Product.objects.filter(is_available=True).order_by('-created_date', '-id')

    product_count = products.count()
    paginator = Paginator(products, 6)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)


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