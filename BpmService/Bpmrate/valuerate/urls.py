
from django.urls import path
from valuerate import views

urlpatterns = [
    path('index/', views.index),
    path('rat/', views.rat),
    path('clu/', views.clu),
    path('cal/', views.cal),
    path('mda/', views.Mda),
    path('rec/', views.rec)
]
