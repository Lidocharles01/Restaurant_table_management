# urls.py
from django.urls import path
from .views import *

app_name = 'TableApp'

urlpatterns = [
    path('', home, name='home'),
    path('shop_home/', shop_home, name="shop_home"),
    path('table/', table, name="table"),
    path('take/', take, name="take"),
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('signout/', signout, name="signout"),
    path('categories/', category_list, name='category_list'),
    path('categories/add/', add_category, name='add_category'),
    path('categories/add_item/', add_item, name='add_item'),
    path('categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', delete_category, name='delete_category'),
    path('all_items/', all_items, name='all_items'),
    path('items/<int:item_id>/edit/', edit_item, name='edit_item'),
    path('items/<int:item_id>/delete/', delete_item, name='delete_item'),
    path('items/<int:item_id>/details/', item_details, name='item_details'),
    path('items/<int:item_id>/add_to_booking/', add_to_booking, name='add_to_booking'),
    path('booking/<int:item_id>/', booking, name='booking'),
    path('home-delivery/', home_delivery, name='home_delivery'),

]
