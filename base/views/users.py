import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


# ======================================================
# CREATE USER (REGISTER)
# role is decided from URL, NOT from body
# ======================================================
@api_view(['POST'])
def create_user(request, role):
    data = request.data

    if role not in ['buyer', 'seller']:
        return JsonResponse({"error": "Invalid role"}, status=400)

    if User.objects.filter(email=data['email']).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    user = User.objects.create(
        email=data['email'],
        username=data['email'],   # FIX: username must be unique and set
        name=data.get('name', ''),
        phone=data.get('phone', ''),
        role=role
    )
    user.set_password(data['password'])
    user.save()

    return JsonResponse({
        "message": f"{role.capitalize()} created successfully",
        "id": user.id
    })


# ======================================================
# GET ALL USERS
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "created_at": user.created_at
        })

    return JsonResponse(data, safe=False)


# ======================================================
# GET SINGLE USER (Only himself)
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):

    if request.user.id != user_id:
        return JsonResponse({"error": "Not allowed"}, status=403)

    user = request.user

    return JsonResponse({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at
    })


# ======================================================
# UPDATE USER (Only himself)
# ======================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):

    if request.user.id != user_id:
        return JsonResponse({"error": "Not allowed"}, status=403)

    user = request.user
    data = request.data

    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)

    if 'password' in data:
        user.set_password(data['password'])

    user.save()

    return JsonResponse({'message': 'User updated successfully'})


# ======================================================
# DELETE USER (Only himself)
# ======================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):

    if request.user.id != user_id:
        return JsonResponse({"error": "Not allowed"}, status=403)

    request.user.delete()

    return JsonResponse({'message': 'User deleted successfully'})