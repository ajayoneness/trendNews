from django.urls import path
from . import views

urlpatterns = [

    path('',views.home,name=""),
    path('process_string/', views.ProcessStringView.as_view(), name='process_string'),
    path('getnewstopic/', views.getNewsTopic.as_view(), name='getnewstopic'),
]
