from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem
from store.models import Product

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

def _cart_items_for_request(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user, is_active=True)
    return CartItem.objects.filter(cart__cart_id=_cart_id(request), is_active=True)

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    if request.method != 'POST':
        return redirect(product.get_absolute_url())

    active_variations = product.variations.filter(is_active=True)
    selected_ids = request.POST.getlist('variation_ids')
    required_categories = set(active_variations.values_list('variation_category', flat=True).distinct())
    selected_variations = list(active_variations.filter(id__in=selected_ids))
    selected_categories = [variation.variation_category for variation in selected_variations]
    if required_categories and (
        len(selected_variations) != len(required_categories)
        or len(selected_ids) != len(required_categories)
        or set(selected_categories) != required_categories
    ):
        messages.error(request, 'Please select one valid option for each product variation.')
        return redirect(product.get_absolute_url())

    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    selected_variation_ids = {variation.id for variation in selected_variations}
    cart_item = None
    existing_items = CartItem.objects.filter(product=product, is_active=True)
    if request.user.is_authenticated:
        existing_items = existing_items.filter(user=request.user)
    else:
        existing_items = existing_items.filter(cart=cart)

    for existing_item in existing_items.prefetch_related('variations'):
        if set(existing_item.variations.values_list('id', flat=True)) == selected_variation_ids:
            cart_item = existing_item
            break

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            user=request.user if request.user.is_authenticated else None,
            quantity=1,
        )
        cart_item.variations.set(selected_variations)

    return redirect('cart') # redirect to the cart page

def increment_cart(request, cart_item_id):
    cart_item = _cart_items_for_request(request).filter(id=cart_item_id).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

def decrement_cart(request, cart_item_id):
    cart_item = _cart_items_for_request(request).filter(id=cart_item_id).first()
    if not cart_item:
        return redirect('cart')
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart(request, cart_item_id):
    cart_item = _cart_items_for_request(request).filter(id=cart_item_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('cart')

def cart(request):
    total = 0
    quantity = 0
    cart_items = _cart_items_for_request(request).select_related('product').prefetch_related('variations')
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

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