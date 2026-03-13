from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from base.models.address import Address
from base.models.orders import Order
from base.models.order_item import OrderItem
from base.models.payment import Payment


# ===================================================
# CREATE ORDER (Buyer Only)
# ===================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can create orders"}, status=403)

    data = request.data

    shipping_address = None

    if 'shipping_address_id' in data:
        shipping_address = get_object_or_404(
            Address,
            id=data['shipping_address_id'],
            user=request.user
        )

    order = Order.objects.create(
        buyer=request.user,
        shipping_address=shipping_address,
        total_amount=0,
        status='pending'
    )

    Payment.objects.create(
        order=order,
        method='cod',
        amount=0,
        status='pending'
    )

    return JsonResponse({
        'message': 'Order created with COD',
        'id': order.id
    })


# ===================================================
# GET ORDERS
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):

    user = request.user

    if user.role == 'buyer':
        orders = Order.objects.filter(buyer=user)

    elif user.role == 'seller':
        orders = Order.objects.filter(
            orderitem__product__seller=user
        ).distinct()

    data = []

    for order in orders:
        data.append({
            "id": order.id,
            "buyer": order.buyer.id,
            "shipping_address": order.shipping_address.id if order.shipping_address else None,
            "total_amount": str(order.total_amount),
            "status": order.status,
            "created_at": order.created_at
        })

    return JsonResponse(data, safe=False)


# ===================================================
# GET SINGLE ORDER
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, pk):

    order = get_object_or_404(Order, id=pk)

    if request.user.role == 'buyer' and order.buyer != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    if request.user.role == 'seller':
        if not OrderItem.objects.filter(
                order=order,
                product__seller=request.user).exists():
            return JsonResponse({"error": "Not allowed"}, status=403)

    return JsonResponse({
        "id": order.id,
        "buyer": order.buyer.id,
        "shipping_address": order.shipping_address.id if order.shipping_address else None,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "created_at": order.created_at
    })


# ===================================================
# UPDATE ORDER
# ===================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order(request, pk):

    order = get_object_or_404(Order, id=pk)
    user = request.user
    data = request.data

    if order.status == "delivered":
        return JsonResponse({"error": "Order completed"}, status=400)

    if user.role == "buyer" and order.buyer == user:

        if 'shipping_address_id' in data:

            address = get_object_or_404(
                Address,
                id=data['shipping_address_id'],
                user=user
            )

            order.shipping_address = address
            order.save()

            return JsonResponse({
                "message": "Shipping address updated"
            })

    if user.role == "seller":

        seller_has_product = OrderItem.objects.filter(
            order=order,
            product__seller=user
        ).exists()

        if seller_has_product and 'status' in data:

            new_status = data['status']

            if order.status == "pending" and new_status == "shipped":
                order.status = "shipped"

            elif order.status == "shipped" and new_status == "delivered":

                order.status = "delivered"

                payment = Payment.objects.get(order=order)
                payment.status = "completed"
                payment.amount = order.total_amount
                payment.save()

            else:
                return JsonResponse({
                    "error": "Invalid status change"
                }, status=400)

            order.save()

            return JsonResponse({
                "message": "Order status updated"
            })

    return JsonResponse({"error": "Not allowed"}, status=403)


# ===================================================
# DELETE ORDER
# ===================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):

    order = get_object_or_404(Order, id=pk)

    if request.user.role != 'buyer' or order.buyer != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    if order.status == "delivered":
        return JsonResponse({"error": "Cannot delete delivered order"}, status=400)

    order.delete()

    return JsonResponse({
        "message": "Order deleted"
    })