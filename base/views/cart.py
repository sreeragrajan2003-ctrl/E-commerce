from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base.models.cart import Cart
from base.models.product import Product


# ===================================================
# ADD TO CART (Buyer Only)
# ===================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can use cart"}, status=403)

    data = request.data

    product = get_object_or_404(Product, id=data['product_id'])

    # Check stock before adding
    requested_qty = data.get('quantity', 1)
    if product.stock < requested_qty:
        return JsonResponse({"error": "Not enough stock available"}, status=400)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += requested_qty
    else:
        cart_item.quantity = requested_qty

    cart_item.save()

    return JsonResponse({
        "message": "Added to cart",
        "cart_id": cart_item.id,
        "quantity": cart_item.quantity
    })


# ===================================================
# GET CART (Only Own Cart)
# FIX: removed unused user_id URL param — uses request.user
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can view cart"}, status=403)

    cart_items = Cart.objects.filter(user=request.user).select_related('product')

    data = []
    total = 0

    for item in cart_items:
        subtotal = item.product.price * item.quantity
        total += subtotal

        data.append({
            "cart_id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "price": str(item.product.price),
            "quantity": item.quantity,
            "subtotal": str(subtotal)
        })

    return JsonResponse({
        "items": data,
        "total_amount": str(total)
    })


# ===================================================
# UPDATE CART ITEM (Own Only)
# ===================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart(request, pk):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can update cart"}, status=403)

    cart_item = get_object_or_404(Cart, id=pk, user=request.user)

    data = request.data
    new_quantity = data.get('quantity', cart_item.quantity)

    if new_quantity < 1:
        return JsonResponse({"error": "Quantity must be at least 1"}, status=400)

    if cart_item.product.stock < new_quantity:
        return JsonResponse({"error": "Not enough stock available"}, status=400)

    cart_item.quantity = new_quantity
    cart_item.save()

    return JsonResponse({"message": "Cart updated", "quantity": cart_item.quantity})


# ===================================================
# DELETE CART ITEM (Own Only)
# ===================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can remove cart items"}, status=403)

    cart_item = get_object_or_404(Cart, id=pk, user=request.user)
    cart_item.delete()

    return JsonResponse({"message": "Item removed from cart"})


# ===================================================
# CLEAR CART (Own Only)
# FIX: removed unused user_id URL param — uses request.user
# ===================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can clear cart"}, status=403)

    Cart.objects.filter(user=request.user).delete()

    return JsonResponse({"message": "Cart cleared"})