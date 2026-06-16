from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 


urlpatterns = [
    path('', views.home, name='home'),   # homepage → shows categories

    path('products/', views.product_list, name='product_list'),

    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('category/<int:category_id>/', views.category_products, name='category_products'),

    path('cart/', views.cart_detail, name='cart_detail'),
      path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
     path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('address/', views.address, name='address'),
    path('review-order/', views.review_order, name='review_order'),
    path('success/', views.payment_success, name='payment_success'),



]
