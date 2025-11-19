
from collections import Counter  # For building frequency table of symbols
from bitarray import bitarray     # Efficient bit array manipulation
import heapq                      # min-heap for Huffman tree construction


# -------------------------------------------------- Compressing Functions ----------------------------------------------------------

class Node:
    """
    Node class for Huffman Tree.
    symbol: Byte value for leaf nodes, None for internal nodes
    freq: Frequency of symbol or sum of child frequencies
    left, right: Child nodes
    """
    def __init__(self, symbol, freq, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq  # Comparison for heap operations


def build_huffman_tree(freq_table):
    """
    Builds a Huffman tree from a frequency table using a min-heap.
    Returns: Root node of Huffman tree
    """
    if not freq_table:
        return None

    heap = []
    for symbol, frequency in freq_table.items():
        heapq.heappush(heap, Node(symbol, frequency))  # Push leaf nodes to heap
    
    while len(heap) > 1:
        node1 = heapq.heappop(heap)  # Pop two nodes with smallest frequency
        node2 = heapq.heappop(heap)
        merged = Node(symbol=None, freq=node1.freq + node2.freq, left=node1, right=node2)  # Merge them
        heapq.heappush(heap, merged)  # Push merged node back

    return heap[0]  # Root node


def generate_huffman_code(node, current_node, code_map):
    """
    Recursively traverses Huffman tree to generate codes for each symbol.
    Stores symbol → code mapping in code_map dictionary.
    """
    if node is None:
        return
    
    if node.symbol is not None:
        if current_node == "":
            code_map[node.symbol] = "0"  # Edge case: only one symbol
        else:
            code_map[node.symbol] = current_node
        return
    
    # Recursion to the left of root node
    generate_huffman_code(node.left, current_node + "0", code_map)

    # Recursion to the right of root node
    generate_huffman_code(node.right, current_node + "1", code_map)


def encode_data_to_bitarray(data: bytes, code_map: dict) -> bytes:
    """
    Encodes input data using Huffman code map into a bitarray and packs it into bytes.
    Returns: bytes containing the compressed data.
    """
    bits = bitarray()
    for b in data:
        bits.extend(code_map[b])  # Append Huffman code for each byte

    pad_len = (8 - len(bits) % 8) % 8  # Pad to make multiple of 8
    bits.extend("0" * pad_len)

    return bytes([pad_len]) + bits.tobytes()  # Prepend padding length


def compress_huffman(data: bytes, ext: str = "txt") -> bytes: 
    """
    Compresses input data using Huffman coding.
    Returns: Bytes containing header + compressed payload.
    """
    if not data:
        return b''

    # Preparing Header
    header = bytearray(b"HUF1")

    # Building frequency table
    freq_table = Counter(data)

    # Encode Extension length and bytes
    ext_bytes = ext.encode("utf-8")
    if len(ext_bytes) > 10:
        raise ValueError("Extension too long")
    
    header += bytes([len(ext_bytes)]) + ext_bytes

    # Building header

    k = len(freq_table)
    header += k.to_bytes(2, 'big')
    for symbol, freq in freq_table.items():
        header += bytes([symbol]) + freq.to_bytes(8, 'big')

    # Build Payload
    root = build_huffman_tree(freq_table)
    code_map = {}
    generate_huffman_code(root, "", code_map)
    payload = encode_data_to_bitarray(data, code_map)

    return bytes(header + payload)

# -------------------------------------------------- Decompressing Functions ----------------------------------------------------------

def load_frequency_table(source, from_bytes=False):
    """
    Loads the Huffman frequency table and payload from a compressed file or byte data.
    Returns: freq_table (dict), offset (int), payload_bytes (bytes), extension (str)
    """

    if from_bytes:
        data = source  # Use bytes directly
    else:
        with open(source, 'rb') as file:
            data = file.read()  # Read file as bytes
    
    if len(data) < 6:
        raise ValueError("File too short to be a valid HUF file")  # File must be at least header + some data

    signature = data[:4]
    if signature != b"HUF1":
        raise ValueError("Invalid file format — missing signature")  # Verify signature        

    # Read the extension
    ext_len = data[4]
    ext = data[5:5 + ext_len].decode('utf-8')

    offset = 5 + ext_len
    k = int.from_bytes(data[offset:offset + 2], 'big')  # Number of unique symbols
    offset += 2

    freq_table = {}
    for _ in range(k):
        symbol = data[offset]  # Symbol (byte)
        freq = int.from_bytes(data[offset + 1: offset + 9], 'big')  # Frequency (8 bytes)
        freq_table[symbol] = freq
        offset += 9

    payload_bytes = data[offset:]

    if len(payload_bytes) == 0:
        print("[WARNING] Payload bytes length is 0 — there is no compressed payload.")  # Edge case warning

    return freq_table, offset, payload_bytes, ext

def decode_data(encoded_bits, root):
    """
    Decodes Huffman-encoded bit string using the Huffman tree.
    Returns: Decoded bytes.
    """
    if not encoded_bits or root is None:
        return b''

    # Edge case: only one symbol in the tree
    if root.left is None and root.right is None:
        return bytes([root.symbol] * len(encoded_bits))

    decoded_bytes = []          # List to store the decoded bytes
    current = root              # Start traversal from the root of Huffman tree

    for bit in encoded_bits:    # Iterate over each bit in the encoded bit string
        if bit == "0":
            current = current.left   # Move left for '0'
        else:
            current = current.right  # Move right for '1'
        
        if current.symbol is not None:  # Reached a leaf node (complete symbol)
            decoded_bytes.append(current.symbol)  # Append the decoded byte
            current = root                      # Reset to root for next symbol
    
    return bytes(decoded_bytes)

def decompress_huffman(data: bytes) -> bytes:
    """
    Decompresses Huffman-compressed bytes.
    Returns: Tuple of decoded bytes and original file extension.
    """
    if not data:
        raise ValueError("No data to decompress")

    try:
        # Load frequency table, header info, payload, and file extension
        freq_table, _, payload_bytes, ext = load_frequency_table(data, from_bytes=True)

        # Rebuild Huffman tree from frequency table
        root = build_huffman_tree(freq_table)
        if root is None:
            raise ValueError("Huffman tree could not be built — invalid compressed data.")

        # Extract padding info and reconstruct bitarray from payload
        pad_len = payload_bytes[0]
        bits = bitarray()
        bits.frombytes(payload_bytes[1:])

        if pad_len: 
            bits = bits[: -pad_len]

        # Decode the bitarray using the Huffman tree
        decoded_data = decode_data(bits.to01(), root)
        return decoded_data, ext
      
    except Exception as e:
        raise ValueError(f"Decompression failed: {str(e)}")


# ---------------------------------------------------- Calculation Compression Ratio -----------------------------------------------

def calculate_compression_ratio(original_size, compressed_size):
    """
    Calculates compression ratio as a percentage.
    """
    if not isinstance(original_size, (int, float)) or not isinstance(compressed_size, (int, float)):
        raise TypeError("Sizes must be numeric values.")
    if original_size <= 0:
        return 0.0

    ratio = (1 - compressed_size / original_size) * 100
    return round(ratio, 2)
