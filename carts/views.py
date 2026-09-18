from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem
from store.models import Product

# Create your views here.
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        cart_item.save()

    return redirect('cart') # redirect to the cart page

def decrement_cart(request, product_id):
    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
    if not cart:
        return redirect('cart')
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if not cart_item:
        return redirect('cart')
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
    if cart:
        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
    return redirect('cart')

def cart(request):
    total = 0
    quantity = 0
    cart_items = []
    cart_id = _cart_id(request)

    try:
        cart = Cart.objects.get(cart_id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).select_related('product')
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    tax = (2 * total) / 100
    grand_total = total + tax
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)