from django.urls import path
from . import views

urlpatterns = [
    # Authentication and User Management
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('change_mpin/', views.change_mpin, name='change_mpin'),
    path('get_new_token/', views.get_new_token, name='get_new_token'),

    #user info
    path('user_info/', views.user_info, name='user_info'),
    path('user_tournaments/', views.user_tournaments, name='user_tournaments'),


    # Tournament Management
    path('tournaments/', views.tournaments, name='tournaments'),
    path('book_slot/<int:pk>/', views.book_slot, name='book_slot'),
    path('create_team/', views.create_team, name='create_team'),

    # Wallet Management
    path('wallet/', views.wallet, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('match_details/<int:pk>/', views.match_details, name='match_details'),

    # Staff Management
    path('stats/<int:tournament>/<int:match>', views.edit_stats, name='stats'),
    path('is_staff', views.is_staff, name='is_staff')
]
