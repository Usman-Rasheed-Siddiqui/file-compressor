
from utility import build_frequency_table, read_binary_file, pad_bitstring, bitstring_to_bytes, save_frequency_table, calculate_compression_ratio, delta_encode, rle_encode, load_frequency_table, bytes_to_bitstring, remove_padding, write_binary_file, rle_decode, delta_decode, format_size
import os
import heapq

class Node:
    def __init__(self, symbol, freq, left = None, right = None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(freq_table):
    
    if not freq_table:
        return None

    heap = []
    for symbol, frequency in freq_table.items():
        heapq.heappush(heap, Node(symbol, frequency))
    
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(symbol = None, freq= node1.freq + node2.freq, left = node1, right = node2)
        heapq.heappush(heap, merged)

    return heap[0]

def generate_huffman_code(node, current_node, code_map):
    
    if node is None:
        return
    
    if node.symbol is not None:
        code_map[node.symbol] = current_node
        return
    
    # Recursion to the left of root node
    generate_huffman_code(node.left, current_node + "0", code_map)

    # Recursion to the right of root node
    generate_huffman_code(node.right, current_node + "1", code_map)

def encode_data(data, code_map):

    if not data:
        return ""

    bitstring_list = []

    for byte in data:
        code = code_map[byte]
        bitstring_list.append(code)


    return "".join(bitstring_list)

def decode_data(encoded_bits, root):

    if not encoded_bits or root is None:
        return b''

    decoded_bytes = []
    current = root
    for bit in encoded_bits:
        if bit == "0":
            current = current.left
        else:
            current = current.right
        
        if current.symbol is not None:
            decoded_bytes.append(current.symbol)
            current = root
    
    return bytes(decoded_bytes)

def compress(input_path, output_path):

    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    data = read_binary_file(input_path)
    if data is None or not data:
        print("Empty or invalid file — nothing to compress.")
        return 0.0
    
    original_size = len(data)
    print(f"Original Size: {format_size(original_size)} ({original_size} bytes) ")

    # Applying Delta
    _, ext = os.path.splitext(input_path)
    use_delta = not ext.lower() in ['.txt', '.log', '.pdf']
    pre_data = delta_encode(data) if use_delta else data
    # delta_data = delta_encode(data)
    use_rle = False
    rle_test = rle_encode(pre_data)
    rle_data = rle_test if len(rle_test) < len(pre_data) else pre_data
    use_rle = len(rle_test) < len(pre_data)
    print(f"DEBUG: Use delta: {use_delta}, Use RLE: {use_rle}, Pre len: {len(rle_data)}")

    # RLE Data
    # rle_data = delta_data
    # if len(rle_encode(delta_data)) < len(delta_data):
    #     rle_data = rle_encode(delta_data)
    #     use_rle = True

    # Building header
    freq_table = build_frequency_table(rle_data)
    header = bytearray(b"HUF1")
    header += bytes([1 if use_rle else 0, 1 if use_delta else 0])
    k = len(freq_table)
    header += k.to_bytes(2, 'big')
    for symbol, freq in freq_table.items():
            header += bytes([symbol]) + freq.to_bytes(8, 'big')

    header_size = len(header)

    # Build Payload
    root = build_huffman_tree(freq_table)
    code_map = {}
    generate_huffman_code(root, "", code_map)
    bitstring = encode_data(rle_data, code_map)
    padded = pad_bitstring(bitstring)
    payload = bitstring_to_bytes(padded)
    total_compressed = header_size + len(payload)

    if total_compressed < original_size or original_size > 1024 * 1024:
        # Use compressed
        save_frequency_table(output_path, freq_table, payload, use_compression= True, use_rle = use_rle, use_delta=use_delta)
        compressed_size = total_compressed
        mode = "compressed" + (" (forced)" if original_size > 1024 * 1024 and total_compressed >= original_size else "")

    else:
        save_frequency_table(output_path, {}, data, use_compression=False)
        compressed_size = 4 + original_size
        mode = "uncompressed (fallback)"
        print("Compression would inflate; storing original.")

    ratio = calculate_compression_ratio(original_size, compressed_size)
    print(f"Compressed Size: {format_size(compressed_size)} ({compressed_size} bytes)")
    print(f"Mode: {mode} | Compression ratio: {ratio:.2f}%")
    return ratio


def decompress(input_path, output_path):
    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    try:
        freq_table, _, payload_bytes, use_compression, use_rle, use_delta = load_frequency_table(input_path)
        print(f"DEBUG: Payload len: {len(payload_bytes) if payload_bytes else 0} bytes")
        print(f"DEBUG: Use compression: {use_compression}, Use RLE: {use_rle}, Use delta: {use_delta}")

        if not use_compression:
            if payload_bytes:
                write_binary_file(output_path, payload_bytes)
            print(f"✅ Decompressed successfully (uncompressed mode): {output_path}")
            return
        
        root = build_huffman_tree(freq_table)
        bitstring = bytes_to_bitstring(payload_bytes)
        print(f"DEBUG: Bitstring len: {len(bitstring)} bits")  # NEW: Add this
        print(f"DEBUG: First 8 bits: '{bitstring[:8]}'")  # NEW: To diagnose pad
        if len(bitstring) == 0:
            decoded_data = b''
        else:

            clean_bits = remove_padding(bitstring)
            print(f"DEBUG: Clean bits len: {len(clean_bits)} bits")  # NEW
            decoded_data = decode_data(clean_bits, root)
        print(f"DEBUG: Huffman decoded len: {len(decoded_data)} bytes")  # NEW

        post_data = decoded_data
        if use_rle:
            post_data = rle_decode(decoded_data)
            print(f"DEBUG: RLE decoded len: {len(post_data)} bytes")  # NEW

        if use_delta:
            original_data = delta_decode(post_data)
            print(f"DEBUG: Delta decoded len: {len(original_data)} bytes")
        else:
            original_data = post_data
        
        orig_file = input_path.replace('.huf', '.txt') if input_path.endswith('.huf') else None
        orig_len = len(read_binary_file(orig_file) or b'') if orig_file else 'N/A'
        print(f"DEBUG: Final decoded len: {len(original_data)} bytes (original ~{orig_len})")

        write_binary_file(output_path, original_data)
        print(f"✅ Decompressed successfully: {output_path}")
    
    except Exception as e:
        print(f"❌ Decompression failed: {e}")


import time
start = time.time()
ratio = compress('sample_image.jpg', 'sample.huf')                 
end = time.time()
print(f"Compression ratio: {ratio:.2f}%")
print(f"Time taken: {end - start}s")

start = time.time()
decompress('sample.huf', 'sample_copy.jpg')
end = time.time()
print(f"Time taken: {end - start}s")

import filecmp

BASE_DIR = os.path.dirname(__file__)  # folder of this script
input_path = os.path.join(BASE_DIR, 'sample_image.jpg')
output_path = os.path.join(BASE_DIR, 'sample_copy.jpg')

print("Original vs. Decompressed: Identical?", filecmp.cmp(input_path, output_path))
