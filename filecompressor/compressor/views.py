from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse

import os

from .algorithm import (
    compress_huffman,
    decompress_huffman,
    compress_bmp,
    decompress_bmp,
)

# Create your views here.

def home(request):
    return render(request, "compressor/home.html")

def compressor_text(request):

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('text_compressor')

        if not uploaded_file.name.endswith(".txt"):
            messages.error(request, "Only .txt files are allowed ❌")
            return redirect('text_compressor')


        original_text = uploaded_file.read()
        compressed_data = compress_huffman(original_text)

        messages.success(request, "File compressed successfully! ✅")

        filename, _ = os.path.splitext(uploaded_file.name)

        response = HttpResponse(
            compressed_data,
            content_type = "application/octet-stream"
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{filename}.huff"'
        )

        return response
    
    return render(request, 'compressor/text/compressor.html')


def decompressor_text(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('text_decompressor')

        if not uploaded_file.name.endswith(".huff"):
            messages.error(request, "Only .huff compressed files allowed ❌")
            return redirect('text_decompressor')


        compressed_data = uploaded_file.read()
        decompressed_data = decompress_huffman(compressed_data)

        messages.success(request, "File decompressed successfully! ✅")

        filename, _ = os.path.splitext(uploaded_file.name)

        response = HttpResponse(
            decompressed_data,
            content_type = "application/octet-stream"
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{filename}.txt"'
        )

        return response
    
    return render(request, 'compressor/text/decompressor.html')



def compressor_bmp(request):

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('bmp_compressor')

        if not uploaded_file.name.lower().endswith(".bmp"):
            messages.error(request, "Only .bmp files are allowed ❌")
            return redirect('bmp_compressor')


        original_bmp = uploaded_file.read()
        compressed_data = compress_bmp(original_bmp)

        messages.success(request, "File compressed successfully! ✅")

        filename, _ = os.path.splitext(uploaded_file.name)

        response = HttpResponse(
            compressed_data,
            content_type = "application/octet-stream"
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{filename}.huff"'
        )

        return response
    
    return render(request, 'compressor/bmp/compressor.html')


def decompressor_bmp(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('bmp_decompressor')

        if not uploaded_file.name.endswith(".huff"):
            messages.error(request, "Only .huff compressed files allowed ❌")
            return redirect('bmp_decompressor')


        compressed_data = uploaded_file.read()
        decompressed_data = decompress_bmp(compressed_data)

        messages.success(request, "File decompressed successfully! ✅")

        filename, _ = os.path.splitext(uploaded_file.name)

        response = HttpResponse(
            decompressed_data,
            content_type = "application/octet-stream"
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{filename}.bmp"'
        )

        return response
    
    return render(request, 'compressor/bmp/decompressor.html')