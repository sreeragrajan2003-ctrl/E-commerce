from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from base.models.category import Category


# ======================================================
# CREATE CATEGORY (Only Seller)
# ======================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only sellers can create category"}, status=403)

    name = request.data.get('name')

    category = Category.objects.create(name=name)

    return JsonResponse({
        'message': 'Category created successfully',
        'id': category.id
    })


# ======================================================
# GET ALL CATEGORIES (Public)
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):

    search = request.GET.get('search', '')

    if search:
        categories = Category.objects.filter(name__icontains=search)
    else:
        categories = Category.objects.all()

    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name
        })

    return JsonResponse(data, safe=False)


# ======================================================
# GET SINGLE CATEGORY (Public)
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category(request, pk):

    category = get_object_or_404(Category, id=pk)

    return JsonResponse({
        "id": category.id,
        "name": category.name
    })


# ======================================================
# UPDATE CATEGORY (Only Seller)
# ======================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only sellers can update category"}, status=403)

    category = get_object_or_404(Category, id=pk)

    category.name = request.data.get('name', category.name)
    category.save()

    return JsonResponse({
        'message': 'Category updated successfully'
    })


# ======================================================
# DELETE CATEGORY (Only Seller)
# ======================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request, pk):

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only sellers can delete category"}, status=403)

    category = get_object_or_404(Category, id=pk)
    category.delete()

    return JsonResponse({
        'message': 'Category deleted successfully'
    })
