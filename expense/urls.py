from django.urls import path
from . import views

urlpatterns=[
    path('add',views.add_expense),
    path('retrieve/<int:user_id>',views.get_individual_expenses,name='get_individual_expenses'),
    path('retrieveAll',views.get_overall_expenses,name='get_overall_expenses'),
    path('getBalanceSheet/<int:user_id>',views.balance_sheet,name='balance_sheet')
]