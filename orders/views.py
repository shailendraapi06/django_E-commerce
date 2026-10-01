from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from carts.views import _cart_items_for_request
from .forms import OrderForm
from .models import Order, OrderProduct, Payment


def _cart_summary(cart_items):
    subtotal = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal('0.00'),
    )
    tax = (subtotal * Decimal('0.02')).quantize(Decimal('0.01'))
    return {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': subtotal + tax,
    }


def _order_context(request, form, cart_items):
    context = _cart_summary(cart_items)
    context['form'] = form
    return context


@login_required
def checkout(request):
    cart_items = _cart_items_for_request(request).select_related('product').prefetch_related('variations')
    if not cart_items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    form = OrderForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone': request.user.phone_number,
    })
    return render(request, 'orders/checkout.html', _order_context(request, form, cart_items))


@login_required
@require_POST
def place_order(request):
    cart_items = _cart_items_for_request(request).select_related('product').prefetch_related('variations')
    if not cart_items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    form = OrderForm(request.POST)
    if not form.is_valid():
        return render(request, 'orders/checkout.html', _order_context(request, form, cart_items))

    totals = _cart_summary(cart_items)
    with transaction.atomic():
        payment = Payment.objects.create(
            user=request.user,
            payment_method=Payment.CASH_ON_DELIVERY,
            amount_paid=totals['grand_total'],
        )
        order = form.save(commit=False)
        order.user = request.user
        order.payment = payment
        order.order_total = totals['subtotal']
        order.tax = totals['tax']
        order.grand_total = totals['grand_total']
        order.is_ordered = True
        order.save()

        for cart_item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product.price,
                ordered=True,
            )
            order_product.variations.set(cart_item.variations.all())

        cart_items.delete()

    return redirect('order_complete', order_number=order.order_number)


@login_required
def order_complete(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product', 'items__variations'),
        order_number=order_number,
        user=request.user,
        is_ordered=True,
    )
    return render(request, 'orders/order_complete.html', {'order': order})