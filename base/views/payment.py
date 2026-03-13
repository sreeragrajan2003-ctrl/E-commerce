from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base.models.payment import Payment


# ===================================================
# GET PAYMENTS
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payments(request):

    if request.user.role == 'buyer':
        payments = Payment.objects.filter(order__buyer=request.user)
    else:
        payments = Payment.objects.all()

    data = []

    for payment in payments:
        data.append({
            "id": payment.id,
            "order_id": payment.order.id,
            "method": payment.method,
            "status": payment.status,
            "created_at": payment.created_at
        })

    return JsonResponse(data, safe=False)


# ===================================================
# GET SINGLE PAYMENT
# ===================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment(request, pk):

    payment = get_object_or_404(Payment, id=pk)

    if payment.order.buyer != request.user and request.user.role != 'seller':
        return JsonResponse({"error": "Not allowed"}, status=403)

    return JsonResponse({
        "id": payment.id,
        "order_id": payment.order.id,
        "method": payment.method,
        "status": payment.status,
        "created_at": payment.created_at
    })


# ===================================================
# UPDATE PAYMENT STATUS (Seller Only)
# ===================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_payment(request, pk):

    payment = get_object_or_404(Payment, id=pk)

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only seller can update payment"}, status=403)

    payment.status = request.data.get('status', payment.status)
    payment.save()

    # 🔥 If payment marked paid → update order automatically
    if payment.status == "paid":
        payment.order.status = "delivered"
        payment.order.save()

    return JsonResponse({"message": "Payment updated"})