
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('compressor/', views.compressor, name='compressor'),
    path('decompressor/', views.decompressor, name='decompressor'),

    path('download_compressed/', views.download_compressed, name='download_compressed'),
    path('download_decompressed/', views.download_decompressed, name='download_decompressed'),
]