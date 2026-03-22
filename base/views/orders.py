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
# FIX: removed `amount=0` from Payment.objects.create — field was dropped in migration 0005
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

    # ✅ Correctly create the Order first
    order = Order.objects.create(
        buyer=request.user,
        shipping_address=shipping_address,
        total_amount=0,
        status='pending'
    )

    # ✅ Then create Payment linked to that order
    Payment.objects.create(
        order=order,
        method='cod',
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

    else:
        return JsonResponse({"error": "Invalid role"}, status=403)

    data = []

    for order in orders:

        order_data = {
            "id": order.id,
            "buyer": order.buyer.id,
            "total_amount": str(order.total_amount),
            "status": order.status,
            "created_at": order.created_at,
        }

        # ✅ Give seller full buyer + address details
        if user.role == 'seller':
            order_data['buyer_info'] = {
                "name": order.buyer.name,
                "email": order.buyer.email,
                "phone": order.buyer.phone or '—',
            }
            if order.shipping_address:
                addr = order.shipping_address
                order_data['shipping_address'] = {
                    "full_name": addr.full_name,
                    "phone": addr.phone,
                    "address_line": addr.address_line,
                    "city": addr.city,
                    "state": addr.state,
                    "pincode": addr.pincode,
                    "country": addr.country,
                }
            else:
                order_data['shipping_address'] = None
        else:
            # Buyer only needs address id
            order_data['shipping_address'] = (
                order.shipping_address.id if order.shipping_address else None
            )

        data.append(order_data)

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

    order_data = {
        "id": order.id,
        "buyer": order.buyer.id,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "created_at": order.created_at,
    }

    # ✅ Full buyer and address info for seller
    if request.user.role == 'seller':
        order_data['buyer_info'] = {
            "name": order.buyer.name,
            "email": order.buyer.email,
            "phone": order.buyer.phone or '—',
        }
        if order.shipping_address:
            addr = order.shipping_address
            order_data['shipping_address'] = {
                "full_name": addr.full_name,
                "phone": addr.phone,
                "address_line": addr.address_line,
                "city": addr.city,
                "state": addr.state,
                "pincode": addr.pincode,
                "country": addr.country,
            }
        else:
            order_data['shipping_address'] = None
    else:
        order_data['shipping_address'] = (
            order.shipping_address.id if order.shipping_address else None
        )

    return JsonResponse(order_data)


# ===================================================
# UPDATE ORDER
# Buyer → update shipping address (only if pending)
# Seller → update status: pending→shipped, shipped→delivered
# ===================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order(request, pk):

    order = get_object_or_404(Order, id=pk)
    user = request.user
    data = request.data

    if order.status == "delivered":
        return JsonResponse({"error": "Order already completed"}, status=400)

    if user.role == "buyer" and order.buyer == user:

        if 'shipping_address_id' in data:

            if order.status != 'pending':
                return JsonResponse(
                    {"error": "Cannot change address after order is shipped"},
                    status=400
                )

            address = get_object_or_404(
                Address,
                id=data['shipping_address_id'],
                user=user
            )
            order.shipping_address = address
            order.save()

            return JsonResponse({"message": "Shipping address updated"})

    if user.role == "seller":

        seller_has_product = OrderItem.objects.filter(
            order=order,
            product__seller=user
        ).exists()

        if not seller_has_product:
            return JsonResponse({"error": "Not allowed"}, status=403)

        if 'status' in data:
            new_status = data['status']

            if order.status == "pending" and new_status == "shipped":
                order.status = "shipped"

            elif order.status == "shipped" and new_status == "delivered":
                order.status = "delivered"

                # Mark payment as completed when delivered
                try:
                    payment = Payment.objects.get(order=order)
                    payment.status = "completed"
                    payment.save()
                except Payment.DoesNotExist:
                    pass

            else:
                return JsonResponse({"error": "Invalid status change"}, status=400)

            order.save()
            return JsonResponse({"message": "Order status updated", "status": order.status})

    return JsonResponse({"error": "Not allowed"}, status=403)


# ===================================================
# DELETE ORDER (Buyer Only, only if pending)
# ===================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):

    order = get_object_or_404(Order, id=pk)

    if request.user.role != 'buyer' or order.buyer != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    if order.status == "delivered":
        return JsonResponse({"error": "Cannot delete delivered order"}, status=400)

    # Restore stock for all items before deleting
    for item in OrderItem.objects.filter(order=order):
        item.product.stock += item.quantity
        item.product.save()

    order.delete()

    return JsonResponse({"message": "Order deleted"})