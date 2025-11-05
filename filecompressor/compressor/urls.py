
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('text_compressor/', views.compressor_text, name='text_compressor'),
    path('text_decompressor/', views.decompressor_text, name='text_decompressor'),
    path('bmp_compressor/', views.compressor_bmp, name='bmp_compressor'),
    path('bmp_decompressor/', views.decompressor_bmp, name='bmp_decompressor'),
]