from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from base.models.product import Product
from base.models.category import Category


# =========================================================
# CREATE PRODUCT (Seller Only)
# =========================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only sellers can create products"}, status=403)

    data = request.data

    category_name = data.get('category')
    category, created = Category.objects.get_or_create(name=category_name)

    product = Product.objects.create(
        seller=request.user,
        category=category,
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )

    return JsonResponse({
        'message': 'Product created',
        'product_id': product.id,
        'category_created': created
    })


# =========================================================
# GET PRODUCTS (Public)
# =========================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):

    search = request.GET.get('search', '')

    if search:
        products = Product.objects.filter(
            name__icontains=search
        ) | Product.objects.filter(
            category__name__icontains=search
        )
    else:
        products = Product.objects.all()

    data = []

    for product in products:
        data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock,
            "seller": product.seller.id,
            "category": product.category.name
        })

    return JsonResponse(data, safe=False)


# =========================================================
# GET SINGLE PRODUCT (Public)
# =========================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request, pk):

    product = get_object_or_404(Product, id=pk)

    return JsonResponse({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "seller": product.seller.id,
        "category": product.category.name
    })


# =========================================================
# UPDATE PRODUCT (Owner Seller Only)
# =========================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):

    product = get_object_or_404(Product, id=pk)

    if request.user.role != 'seller' or product.seller != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    data = request.data

    if 'category' in data:
        category, created = Category.objects.get_or_create(name=data['category'])
        product.category = category

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)

    product.save()

    return JsonResponse({
        "message": "Product updated"
    })


# =========================================================
# DELETE PRODUCT (Owner Seller Only)
# =========================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):

    product = get_object_or_404(Product, id=pk)

    if request.user.role != 'seller' or product.seller != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    product.delete()

    return JsonResponse({
        "message": "Product deleted"
    })


# =========================================================
# SELLER PRODUCTS (Seller Dashboard)
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_products(request):

    if request.user.role != 'seller':
        return JsonResponse({"error": "Only sellers allowed"}, status=403)

    products = Product.objects.filter(seller=request.user)

    data = []

    for product in products:
        data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock,
            "category": product.category.name
        })

    return JsonResponse(data, safe=False)