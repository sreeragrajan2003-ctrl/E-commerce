from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base.models.cart import Cart
from base.models.orders import Order
from base.models.order_item import OrderItem
from base.models.address import Address
from base.models.product import Product


# ===================================================
# CHECKOUT (Buyer Only)
# ===================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can checkout"}, status=403)

    data = request.data

    # 1️⃣ Get shipping address
    shipping_address = get_object_or_404(
        Address,
        id=data['shipping_address_id'],
        user=request.user
    )

    # 2️⃣ Get cart items
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)

    total_amount = 0

    # 3️⃣ Validate stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            return JsonResponse({
                "error": f"Not enough stock for {item.product.name}"
            }, status=400)

        total_amount += item.product.price * item.quantity

    # 4️⃣ Create Order
    order = Order.objects.create(
        buyer=request.user,
        shipping_address=shipping_address,
        total_amount=total_amount,
        status='pending'
    )

    # 5️⃣ Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        # 6️⃣ Reduce stock
        item.product.stock -= item.quantity
        item.product.save()

    # 7️⃣ Clear cart
    cart_items.delete()

    return JsonResponse({
        "message": "Checkout successful",
        "order_id": order.id,
        "total_amount": str(total_amount)
    })