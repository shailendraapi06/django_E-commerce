from .models import Category
from carts.models import CartItem

def menu_links(request):
    links = Category.objects.all()
    cart_count = 0
    if request.session.session_key:
        cart_count = sum(
            item.quantity
            for item in CartItem.objects.filter(
                cart__cart_id=request.session.session_key,
                is_active=True,
            )
        )
    return {'links': links, 'cart_count': cart_count}