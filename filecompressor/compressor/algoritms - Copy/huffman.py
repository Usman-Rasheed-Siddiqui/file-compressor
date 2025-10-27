
from utility import build_frequency_table, read_binary_file, pad_bitstring, bitstring_to_bytes, save_frequency_table, calculate_compression_ratio, delta_encode, rle_encode, load_frequency_table, bytes_to_bitstring, remove_padding, write_binary_file, rle_decode, delta_decode, adaptive_rle
import os, time

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

    nodes = []
    for symbol, frequency in freq_table.items():
        leaf = Node(symbol, frequency)
        nodes.append(leaf)
    
    while len(nodes) > 1:
        nodes = sorted(nodes, key= lambda x: x.freq)
        node1 = nodes.pop(0)
        node2 = nodes.pop(0)
        merged = Node(symbol = None, freq= node1.freq + node2.freq, left = node1, right = node2)

        nodes.append(merged)

    return nodes[0]

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

    encoded_bits = ""

    if not data:
        return ""

    for byte in data:

        code = code_map[byte]
        encoded_bits += f"{code}"

    return encoded_bits

def decode_data(encoded_bits, root):

    decoded_bytes = []
    current = root

    for bit in encoded_bits:
        if bit == "0":
            current = current.left
        elif bit == "1":
            current = current.right
        else:
            raise ValueError(f"Invalid bit: {bit}")

        # SAFETY CHECK
        if current is None:
            raise ValueError("Traversal reached None — corrupted bitstream or padding issue.")

        if current.symbol is not None:
            decoded_bytes.append(current.symbol)
            current = root
    
    return bytes(decoded_bytes)

def compress(input_path, output_path):

    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    data = read_binary_file(input_path)

    if not data:
        print("Empty file — nothing to compress.")
        return


    delta_data = delta_encode(data)
    
    # RLE Data
    rle_data = adaptive_rle(delta_data)

    print(f"[DEBUG] Input bytes: {len(data)} | Delta bytes: {len(delta_data)} | RLE bytes: {len(rle_data)}")

    freq_table = build_frequency_table(rle_data)
    root = build_huffman_tree(freq_table)

    if root is None:
        raise ValueError("Failed to build Huffman tree — empty frequency table.")

    code_map = {}
    generate_huffman_code(root, "", code_map)

    bitstring = encode_data(rle_data, code_map)
    padded = pad_bitstring(bitstring)
    payload = bitstring_to_bytes(padded)

    print(f"[DEBUG] Freq table entries: {len(freq_table)}")
    print(f"[DEBUG] Example entries: {list(freq_table.items())[:10]}")
    save_frequency_table(output_path, freq_table, payload)

    original_size = len(data)
    print("Original Size:", original_size)
    compressed_size = os.path.getsize(output_path)
    print("Compressed Size:", compressed_size)
    
    ratio = calculate_compression_ratio(original_size, compressed_size)
    # print(f"[TIME] Compression finished in {time.time() - start:.2f}s")
    return ratio


def decompress(input_path, output_path):
    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    # Quick check file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    freq_table, payload_offset, payload_bytes = load_frequency_table(input_path)
    print(f"[DEBUG] Loaded {len(freq_table)} symbols from frequency table (payload bytes: {len(payload_bytes)})")

    root = build_huffman_tree(freq_table)
    if root is None:
        raise ValueError("Invalid or empty Huffman tree — cannot decode.")
    
    bitstring = bytes_to_bitstring(payload_bytes)
    clean_bits = remove_padding(bitstring)

    print(f"[DEBUG] First 32 bits: {clean_bits[:32]} ...")
    print(f"[DEBUG] clean_bits type: {type(clean_bits)} length: {len(clean_bits)}")
    print(f"[DEBUG] clean_bits sample: {clean_bits[:64]}")

    decoded_data = decode_data(clean_bits, root)

    rle_decoded = rle_decode(decoded_data)
    original_data = delta_decode(rle_decoded)

    write_binary_file(output_path, original_data)
    print(f"✅ Decompressed successfully: {output_path}")


start = time.time() 
ratio = compress('sample_image.jpg', 'sample_copy.huf')    
print("[TIME] Time Taken:", time.time() - start)            
print(f"[STATS] Total ratio: {ratio:.2f}%")


#decompress('sample_copy.huf', 'sample_decompressed.jpg')

# import filecmp

# BASE_DIR = os.path.dirname(__file__)  # folder of this script
# input_path = os.path.join(BASE_DIR, "sample_image.jpg")
# output_path = os.path.join(BASE_DIR, "sample_decompressed.jpg")

# print("Files identical:", filecmp.cmp(input_path, output_path, shallow=False))





# CHUNKS ONE

    # start = time.time()

    # CHUNK_SIZE = 512 * 1024  # 512 KB
    # total_original = 0
    # total_compressed = 0

    # with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
    #     while chunk := fin.read(CHUNK_SIZE):
    #         delta_data = delta_encode(chunk)
    #         rle_data = adaptive_rle(delta_data)

    #         freq_table = build_frequency_table(rle_data)
    #         root = build_huffman_tree(freq_table)
    #         code_map = {}
    #         generate_huffman_code(root, "", code_map)

    #         bitstring = encode_data(rle_data, code_map)
    #         padded = pad_bitstring(bitstring)
    #         payload = bitstring_to_bytes(padded)

    #         save_frequency_table(output_path, freq_table, payload)
    #         total_original += len(rle_data)
    #         total_compressed += len(payload)