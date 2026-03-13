from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base.models.order_item import OrderItem
from base.models.orders import Order
from base.models.product import Product


# ===================================================
# CREATE ORDER ITEM
# ===================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_item(request):

    if request.user.role != 'buyer':
        return JsonResponse({"error": "Only buyers can add items"}, status=403)

    data = request.data

    order = get_object_or_404(Order, id=data['order_id'], buyer=request.user)
    product = get_object_or_404(Product, id=data['product_id'])

    quantity = data['quantity']

    # 🔴 STOCK CHECK
    if product.stock < quantity:
        return JsonResponse({
            "error": "Not enough stock available"
        }, status=400)

    # 🔥 REDUCE STOCK
    product.stock -= quantity
    product.save()

    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        price=product.price
    )

    # update order total
    total = 0
    items = OrderItem.objects.filter(order=order)

    for item in items:
        total += item.quantity * item.price

    order.total_amount = total
    order.save()

    return JsonResponse({
        "message": "Order item created",
        "order_item_id": order_item.id,
        "total_amount": str(order.total_amount)
    })


# ===================================================
# GET ORDER ITEMS
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_items(request):

    user = request.user

    if user.role == 'buyer':
        items = OrderItem.objects.filter(order__buyer=user)

    elif user.role == 'seller':
        items = OrderItem.objects.filter(product__seller=user)

    data = []

    for item in items:
        data.append({
            "id": item.id,
            "order": item.order.id,
            "product": item.product.name,
            "quantity": item.quantity,
            "price": str(item.price)
        })

    return JsonResponse(data, safe=False)


# ===================================================
# GET SINGLE ORDER ITEM
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_item(request, pk):

    item = get_object_or_404(OrderItem, id=pk)

    if request.user.role == 'buyer':
        if item.order.buyer != request.user:
            return JsonResponse({"error": "Not allowed"}, status=403)

    elif request.user.role == 'seller':
        if item.product.seller != request.user:
            return JsonResponse({"error": "Not allowed"}, status=403)

    return JsonResponse({
        "id": item.id,
        "order": item.order.id,
        "product": item.product.name,
        "quantity": item.quantity,
        "price": str(item.price)
    })


# ===================================================
# UPDATE ORDER ITEM
# ===================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_item(request, pk):

    item = get_object_or_404(OrderItem, id=pk)

    if request.user.role != 'buyer' or item.order.buyer != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    data = request.data

    new_quantity = data.get('quantity', item.quantity)

    product = item.product

    difference = new_quantity - item.quantity

    # 🔴 CHECK STOCK
    if difference > 0 and product.stock < difference:
        return JsonResponse({
            "error": "Not enough stock available"
        }, status=400)

    # 🔥 UPDATE STOCK
    product.stock -= difference
    product.save()

    item.quantity = new_quantity
    item.save()

    # recalc order total
    order = item.order

    total = 0
    items = OrderItem.objects.filter(order=order)

    for i in items:
        total += i.quantity * i.price

    order.total_amount = total
    order.save()

    return JsonResponse({
        "message": "Order item updated",
        "total_amount": str(order.total_amount)
    })
# ===================================================
# DELETE ORDER ITEM
# ===================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order_item(request, pk):

    item = get_object_or_404(OrderItem, id=pk)

    if request.user.role != 'buyer' or item.order.buyer != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    product = item.product

    # 🔥 RESTORE STOCK
    product.stock += item.quantity
    product.save()

    order = item.order
    item.delete()

    # recalc order total
    total = 0
    items = OrderItem.objects.filter(order=order)

    for i in items:
        total += i.quantity * i.price

    order.total_amount = total
    order.save()

    return JsonResponse({
        "message": "Order item deleted",
        "total_amount": str(order.total_amount)
    })