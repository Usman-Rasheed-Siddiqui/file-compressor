
# FOR TEXT COMPRESSION
from collections import Counter
from bitarray import bitarray

from .utility import (
    build_frequency_table, pad_bitstring, bitstring_to_bytes, 
    load_frequency_table, bytes_to_bitstring, remove_padding, encode_data_to_bitarray)
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

    encode = code_map.get
    return "".join(encode(b) for b in data)

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


def compress_huffman(data: bytes) -> bytes: 

    if not data:
        return b''
    
    # Building header
    freq_table = Counter(data)
    header = bytearray(b"HUF1")
    header += bytes([0, 0])
    k = len(freq_table)
    header += k.to_bytes(2, 'big')
    for symbol, freq in freq_table.items():
            header += bytes([symbol]) + freq.to_bytes(8, 'big')

    # Build Payload
    root = build_huffman_tree(freq_table)
    code_map = {}
    generate_huffman_code(root, "", code_map)

    # bitstring = encode_data(data, code_map)
    # padded = pad_bitstring(bitstring)
    # payload = bitstring_to_bytes(padded)

    payload = encode_data_to_bitarray(data, code_map)

    return bytes(header + payload)

def decompress_huffman(data: bytes) -> bytes:
    if not data:
        return b''

    try:
        freq_table, _, payload_bytes, _, _, _ = load_frequency_table(data, from_bytes=True)
        root = build_huffman_tree(freq_table)
        pad_len = payload_bytes[0]
        bits = bitarray()
        bits.frombytes(payload_bytes[1:])

        if pad_len: 
            bits = bits[: -pad_len]

        decoded_data = decode_data(bits.to01(), root)

        # bitstring = bytes_to_bitstring(payload_bytes)
        # clean_bits = remove_padding(bitstring)
        # decoded_data = decode_data(clean_bits, root)

        return decoded_data  
      
    except Exception:
        return b''