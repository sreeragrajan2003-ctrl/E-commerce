from django.urls import path
from base.views.auth import *
from base.views.users import *
from base.views.address import *
from base.views.category import *
from base.views.product import *
from base.views.orders import *
from base.views.order_item import *
from base.views.cart import *
from base.views.payment import *
from base.views.checkout import *

urlpatterns = [

    # ================= USERS =================
    path('users/create/<str:role>/', create_user),
    path('users/', get_users),
    path('users/<int:user_id>/', get_user),
    path('users/update/<int:user_id>/', update_user),
    path('users/delete/<int:user_id>/', delete_user),

    # ================= ADDRESS =================
    path('address/', get_address),
    path('address/create/', create_address),
    path('address/update/<int:address_id>/', update_address),
    path('address/delete/<int:address_id>/', delete_address),

    # ================= CATEGORY =================
    path('category/', get_categories),
    path('category/create/', create_category),          # FIX: 'create/' before '<int:pk>/'
    path('category/<int:pk>/', get_category),
    path('category/update/<int:pk>/', update_category),
    path('category/delete/<int:pk>/', delete_category),

    # ================= PRODUCT =================
    path('product/', get_products),
    path('product/my/', seller_products),               # FIX: 'my/' MUST come before '<int:pk>/'
    path('product/create/', create_product),            # FIX: 'create/' before '<int:pk>/'
    path('product/<int:pk>/', get_product),
    path('product/update/<int:pk>/', update_product),
    path('product/delete/<int:pk>/', delete_product),

    # ================= ORDERS =================
    path('orders/', get_orders),
    path('orders/create/', create_order),               # FIX: 'create/' before '<int:pk>/'
    path('orders/<int:pk>/', get_order),
    path('orders/update/<int:pk>/', update_order),
    path('orders/delete/<int:pk>/', delete_order),

    # ================= ORDER ITEMS =================
    path('order-items/', get_order_items),
    path('order-items/create/', create_order_item),
    path('order-items/<int:pk>/', get_order_item),
    path('order-items/update/<int:pk>/', update_order_item),
    path('order-items/delete/<int:pk>/', delete_order_item),

    # ================= CART =================
    # FIX: removed user_id params — views use request.user internally
    path('cart/', get_cart),
    path('cart/add/', add_to_cart),
    path('cart/update/<int:pk>/', update_cart),
    path('cart/delete/<int:pk>/', delete_cart_item),
    path('cart/clear/', clear_cart),

    # ================= PAYMENTS (COD ONLY) =================
    path('payments/', get_payments),
    path('payments/<int:pk>/', get_payment),
    path('payments/update/<int:pk>/', update_payment),

    # ================= AUTH =================
    path('buyer/register/', buyer_register),
    path('seller/register/', seller_register),
    path('buyer/login/', buyer_login),
    path('seller/login/', seller_login),
    path('token/refresh/', refresh_token),

    # ================= PROTECTED TEST =================
    path('protected/', protected_view),

    # ================= CHECKOUT =================
    path('checkout/', checkout),
]