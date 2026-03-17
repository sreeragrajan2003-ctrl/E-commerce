import json
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from base.models.users import User


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@csrf_exempt
def buyer_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        user = User.objects.create(
            email=data['email'],
            username=data['email'],   # FIX: username must be set
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            role='buyer'
        )
        user.set_password(data['password'])
        user.save()

        tokens = get_tokens_for_user(user)
        return JsonResponse({
            'message': 'Buyer registered successfully',
            'tokens': tokens
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def seller_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        user = User.objects.create(
            email=data['email'],
            username=data['email'],   # FIX: username must be set
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            role='seller'
        )
        user.set_password(data['password'])
        user.save()

        tokens = get_tokens_for_user(user)
        return JsonResponse({
            "message": "Seller registered successfully",
            "tokens": tokens
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def buyer_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        user = authenticate(
            request,
            username=data['email'],   # AbstractUser authenticate uses username field
            password=data['password']
        )

        if user is None or user.role != 'buyer':
            return JsonResponse(
                {"error": "Invalid buyer credentials"},
                status=401
            )

        tokens = get_tokens_for_user(user)
        return JsonResponse({
            "message": "Buyer login successful",
            "tokens": tokens
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def seller_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        user = authenticate(
            request,
            username=data['email'],   # AbstractUser authenticate uses username field
            password=data['password']
        )

        if user is None or user.role != 'seller':
            return JsonResponse(
                {"error": "Invalid seller credentials"},
                status=401
            )

        tokens = get_tokens_for_user(user)
        return JsonResponse({
            "message": "Seller login successful",
            "tokens": tokens
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def refresh_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            refresh = RefreshToken(data['refresh'])
            access_token = str(refresh.access_token)
            return JsonResponse({"access": access_token})

        except (TokenError, InvalidToken):
            return JsonResponse(
                {"error": "Invalid refresh token"},
                status=401
            )

    return JsonResponse({"error": "Method not allowed"}, status=405)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({
        "message": "You are authenticated",
        "user": request.user.email,
        "role": request.user.role
    })