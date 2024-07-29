from django.urls import path
from . import views

urlpatterns=[
    path('create',views.create_user),
    path('get/<int:user_id>',views.get_user)
]