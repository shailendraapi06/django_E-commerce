from django.shortcuts import render, redirect
from .models import Cart, CartItem
from store.models import Product

# Create your views here.
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) # get the product 
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1 # increase the quantity of the cart item
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
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True) # get all the cart items for the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity) # calculate the total price of the cart items
            quantity += cart_item.quantity # calculate the total quantity of the cart items
        tax = (2 * total)/100 # calculate the tax
        grand_total = total + tax # add the tax to the total price
    except objectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)