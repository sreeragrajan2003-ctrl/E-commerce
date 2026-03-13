from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from base.models.address import Address


# ======================================================
# CREATE ADDRESS (Only logged-in user)
# ======================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_address(request):

    data = request.data

    address = Address.objects.create(
        user=request.user,  # 🔐 always logged-in user
        full_name=data['full_name'],
        phone=data['phone'],
        address_line=data['address_line'],
        city=data['city'],
        state=data['state'],
        pincode=data['pincode'],
        country=data['country'],
    )

    return JsonResponse({
        'message': 'Address created successfully',
        'id': address.id
    })


# ======================================================
# GET MY ADDRESSES (Only his addresses)
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_address(request):

    addresses = Address.objects.filter(user=request.user)

    data = []
    for address in addresses:
        data.append({
            "id": address.id,
            "full_name": address.full_name,
            "phone": address.phone,
            "address_line": address.address_line,
            "city": address.city,
            "state": address.state,
            "pincode": address.pincode,
            "country": address.country
        })

    return JsonResponse(data, safe=False)


# ======================================================
# UPDATE ADDRESS (Only if owner)
# ======================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_address(request, address_id):

    address = get_object_or_404(Address, id=address_id)

    # 🔐 check ownership
    if address.user != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    data = request.data

    address.full_name = data.get("full_name", address.full_name)
    address.phone = data.get("phone", address.phone)
    address.address_line = data.get("address_line", address.address_line)
    address.city = data.get("city", address.city)
    address.state = data.get("state", address.state)
    address.pincode = data.get("pincode", address.pincode)
    address.country = data.get("country", address.country)

    address.save()

    return JsonResponse({
        "message": "Address updated successfully"
    })


# ======================================================
# DELETE ADDRESS (Only if owner)
# ======================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_address(request, address_id):

    address = get_object_or_404(Address, id=address_id)

    if address.user != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    address.delete()

    return JsonResponse({
        'message': 'Address deleted successfully'
    })
