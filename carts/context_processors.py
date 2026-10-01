from django.db.models import Sum
from .models import CartItem

def counter(request):
    if 'admin' in request.path:
        return {}

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    elif request.session.session_key:
        cart_items = CartItem.objects.filter(
            cart__cart_id=request.session.session_key,
            is_active=True,
        )
    else:
        return {'cart_count': 0}

    cart_count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0
    return {'cart_count': cart_count}
  