
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse

import os
import time

from .algorithm import (
    compress_huffman,
    decompress_huffman,
    calculate_compression_ratio,
)

# Home Page
def home(request):
    """Render the home page of the compressor web application."""
    return render(request, "compressor/home.html")


def bytes_to_mb(bytes_size):
    """Convert bytes to KB or MB for display in the UI."""
    kb_size = bytes_size / 1024
    if kb_size < 1000:
        return f"{round(kb_size, 2)} KB"
    return f"{round(bytes_size / (1024*1024), 2)} MB"  # MiB


# Compressor View
def compressor(request):
    """
    Handles file compression:
    - Reads uploaded file
    - Compresses using Huffman coding
    - Calculates compression ratio
    - Stores compressed data in session for download
    - Prepares data for template display
    """
    original_text = None
    compressed_data = None
    ratio = None
    start = None
    end = None
    file_name = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('compressor')

        # Check file type for warnings
        ext = os.path.splitext(uploaded_file.name)[1][1:]
        if ext.lower() in ['jpg', 'jpeg', 'png', 'pdf', 'mp3', 'mp4', 'docx', 'pptx', 'xlsx']:
            messages.warning(request, f"Note: Accuracy may be low or in negative for already compressed files like {ext}.\nPrefer compressing uncompressed files")

        # Read file content and compress
        try:
            original_text = uploaded_file.read()
            start = time.time()
            compressed_data = compress_huffman(original_text, ext)
            end = time.time()
            ratio = calculate_compression_ratio(len(original_text), len(compressed_data))

        except Exception as e:
            messages.error(request, f"Compression failed: {e}")
            return redirect('compressor')

        # Prepare filename for download
        name = os.path.splitext(uploaded_file.name)[0]
        huff_filename = f"{name}({ext}).huff"
        request.session['filename'] = huff_filename
        file_name = uploaded_file.name

        # Store compressed data in session
        request.session['compressed_data'] = compressed_data.hex()

        # Display result messages
        if ratio > 0:
            messages.success(request, f"File compressed successfully! Saved {ratio}% ⚡")
        else:
            messages.warning(request, f"Compression unsuccessful. Compression overhead occurred. Ratio: {ratio}%❗")

    context = {
        "ratio": ratio, 
        "original_size": bytes_to_mb(len(original_text)) if original_text else 0, 
        "compressed_size": bytes_to_mb(len(compressed_data)) if compressed_data else 0,
        "time_taken": (end - start) if start and end else None,
        "name": file_name if file_name else None,
    }

    return render(request, 'compressor/compressor.html', context)


# Download the Compressed File
def download_compressed(request):
    """
    Sends the compressed Huffman file to the user for download.
    Retrieves the hex-encoded compressed data and filename from session.
    """

    # Retrieve compressed data and filename from session
    compressed_data_hex = request.session.get('compressed_data')
    filename = request.session.get('filename')

    # If no compressed file exists, show error and redirect
    if not compressed_data_hex:
        messages.error(request, "No compressed file found.")
        return redirect('compressor')

    # Convert hex data back to bytes
    compressed_data = bytes.fromhex(compressed_data_hex)
    name, _ = os.path.splitext(filename)

    # Prepare HTTP response for file download
    response = HttpResponse(
        compressed_data,
        content_type="application/octet-stream"
    )
    response['Content-Disposition'] = f'attachment; filename="{name}.huff"'
    return response


# Decompressor View
def decompressor(request):
    """
    Handles file decompression:
    - Reads uploaded .huff file
    - Decompresses using Huffman decoding
    - Calculates decompression ratio
    - Stores decompressed data in session for download
    - Prepares data for template display
    """
    decompressed_size = None
    compressed_size = None
    ratio = None
    start = None
    end = None
    file_name = None

    if request.method == "POST" and request.FILES.get('file'):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected")
            return redirect('decompressor')

        if not uploaded_file.name.endswith(".huff"):
            messages.error(request, "Only .huff compressed files allowed ❌")
            return redirect('decompressor')

        # Read compressed file and decompress
        try:
            compressed_data = uploaded_file.read()
            start = time.time()
            decompressed_data, ext = decompress_huffman(compressed_data)
            end = time.time()
        except Exception as e:
            messages.error(request, f"Decompression failed: {e}")
            return redirect('decompressor')

        # Calculate sizes and compression ratio
        compressed_size = len(compressed_data)
        decompressed_size = len(decompressed_data)
        ratio = calculate_compression_ratio(compressed_size, decompressed_size)

        # Store decompressed data and prepare filename
        request.session['decompressed_data'] = decompressed_data.hex()
        original_name = uploaded_file.name

        main_name = os.path.splitext(original_name)[0] 
        
        if f"({ext})" in main_name:
            name_without_ext = main_name.replace(f"({ext})", "")
        
        else:
            name_without_ext = main_name    

        decompressed_filename = f"{name_without_ext}.{ext}"

        file_name = uploaded_file.name
        request.session['decompressed_filename'] = decompressed_filename

        messages.success(request, "File decompressed successfully! ✅")

    context = {
        "decompressed_size": bytes_to_mb(decompressed_size) if decompressed_size else 0,
        "compressed_size": bytes_to_mb(compressed_size) if compressed_size else 0,
        "ratio": ratio,
        "time_taken": (end - start) if start and end else None,
        "name": file_name if file_name else None,
    }
    
    return render(request, 'compressor/decompressor.html', context)


# Download the Decompressed File
def download_decompressed(request):
    """
    Sends the decompressed file to the user for download.
    Retrieves the hex-encoded decompressed data and filename from session.
    """
    # Retrieve decompressed data and filename from session
    data_hex = request.session.get('decompressed_data')
    filename = request.session.get('decompressed_filename')
    
    # If no decompressed file exists, show error and redirect
    if not data_hex:
        messages.error(request, "No decompressed file found.")
        return redirect('decompressor')

    # Convert hex data back to bytes
    data = bytes.fromhex(data_hex)

    # Prepare HTTP response for file download
    response = HttpResponse(
        data,
        content_type="application/octet-stream"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Return the response to trigger download
    return response
