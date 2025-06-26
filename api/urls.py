from django.urls import path
from account import views as userauths_views
from store import views as store_views
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
     path('user/token/', userauths_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('user/register/', userauths_views.RegisterView.as_view(), name='register'),
     path('user/password-reset/<str:email>/', userauths_views.PasswordResetEmailView.as_view(), name='password-reset'),
     path('user/password-change/', userauths_views.PasswordChangeView.as_view(), name='password-change'),
     path('user/profile/<user_id>/', userauths_views.ProfileView.as_view(), name='profile'),
     
     # store-view
     path('categories/', store_views.CategoryListAPIView.as_view(), name='category-list'),
    path('products/', store_views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/', store_views.ProductDetailsAPIView.as_view(), name='product-detail'),
    path('cart/', store_views.CartAPIView.as_view(), name='cart-create-list'),
    path('cart/<str:cart_id>/', store_views.CartListView.as_view(), name='cart-list'),
    path('cart/details/<str:cart_id>/', store_views.CartDetailsView.as_view(), name='cart-details'),
    path('cart/<str:cart_id>/item/<int:item_id>/delete/', store_views.CartItemDeleteAPIView.as_view(), name='cart-item-delete'),
    path('order/', store_views.CartOrderAPIView.as_view(), name='cart-order-create'),
    path('checkout/<str:order_oid>/', store_views.StripeCheckoutView.as_view(), name='stripe-checkout'),
    path('payment-success/', store_views.PaymentSuccessView.as_view(), name='payment-success'),
]
