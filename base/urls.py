from django.urls import path, include

from . import views

urlpatterns = [
    # path("", views.slots, name="slots"),
    # path("<int:pk>/", views.book_slot, name="book_slot"),
    # path("login/", views.custom_login, name="login"),
    # path("register/", views.register, name="register"),
    # path("wallet/", views.wallet, name="wallet"),
    # path("wallet/deposit", views.deposit, name="deposit"),
    # path("wallet/withdraw", views.withdraw, name="withdraw"),
    # path("<int:pk>", views.team_details, name="team-details"),
    # path("user/", views.user_info, name="user-info"),
    # path("logout/", views.custom_logout, name="logout"),
    path("api/", include('base.api.urls')),
]