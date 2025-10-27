
import os

# read_binary_files(path)
# write_binary_files(path, data)
# get_file_size(path)
#bitstring_to_bytes(bitstring)
#byte_to_bitstring(data)


def read_binary_file(path):
    try:
        with open(path, "rb") as file:
            byte = file.read()
    
    except FileNotFoundError:
        print("An error occured. Please try again")
        return None

    return byte

def write_binary_file(path, data):

    with open(f"{path}", "wb") as file:
        file.write(data)
        file.flush()
    
    return True

def get_file_size(path):

    try:
        if os.path.exists(path):
            file_info = os.stat(path)
            size_in_bytes = file_info.st_size
            return size_in_bytes

        else:
            return 0

    except OSError:
        print(f"Error accessing {path}")
        return 0


def format_size(size_in_bytes):

    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"


def build_frequency_table(data: bytes):
    
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("Data must be byte-like.")

    frequency_count = {}
    for byte in data:
        frequency_count[byte] = frequency_count.get(byte, 0) + 1   # If found byte + 1 else 0 + 1
    return frequency_count

def bytes_to_bitstring(data: bytes):
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("Data must be in byte-like format")

    bitstring = []
    for byte in data:
        bits =bin(byte)[2:].zfill(8)
        bitstring.append(bits)
    
    return "".join(bitstring)


def bitstring_to_bytes(bitstring):
    if len(bitstring) % 8 != 0:
        raise ValueError( "Bitstring not a multiple of 8")

    string_to_bytes = []

    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i: i+8]
        string_to_bytes.append(int(chunk, 2))

    return bytes(string_to_bytes)


def pad_bitstring(bitstring):
    pad_len = (8-(len(bitstring) % 8)) % 8

    padded_bitstring = bitstring + (pad_len * "0")
    header = format(pad_len, '08b')         # Converting pad_len to it's 8 bit binary form

    full_bitstring = header + padded_bitstring

    return full_bitstring    


def remove_padding(padded_bitstring):
    if len(padded_bitstring) < 8:
        raise ValueError("Corrupted File")

    pad_len = int(padded_bitstring[:8], 2)
    if pad_len == 0:
        cleaned_bitstring = padded_bitstring[8:]
    else:    
        cleaned_bitstring = padded_bitstring[8: -pad_len]

    return cleaned_bitstring


def save_frequency_table(path, freq_table, payload_bytes, use_compression = True, use_rle = False, use_delta = False):
    
    header = bytearray()

    if use_compression:     # Compression Mode

        header += b"HUF1"
        header += bytes([1 if use_rle else 0, 1 if use_delta else 0])
        if not isinstance(freq_table, dict) or len(freq_table) == 0:
            raise ValueError("Incorrect Inputs")
        
        k = len(freq_table)
        header += k.to_bytes(2, 'big')

        for symbol, freq in freq_table.items():
            if not isinstance(symbol, int):
                raise TypeError(f"Symbol {symbol} must be an integer")
            if not (0 <= symbol <= 255):
                raise ValueError(f"Invalid symbol {symbol} — must be between 0 and 255")
            
            header += bytes([symbol])
            header += freq.to_bytes(8, 'big')

    else:       # UnCompressed Mode
        header += b'HUF0'
    output_data = header + payload_bytes
    write_binary_file(path, output_data)


def calculate_compression_ratio(original_size, compressed_size):
    if not isinstance(original_size, (int, float)) or not isinstance(compressed_size, (int, float)):
        raise TypeError("Sizes must be numeric values.")
    if original_size <= 0:
        return 0.0
    
    ratio = ((original_size - compressed_size) / original_size) * 100
    return round(ratio, 2)


def load_frequency_table(path):
    
    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    path = os.path.join(BASE_DIR, path)

    with open(path, 'rb') as file:
        data = file.read()
    
    if not data:
        raise ValueError("Empty file")

    signature = data[:4]

    if signature == b"HUF0":
        return {}, 0, data[4:], False, False, False

    elif signature != b"HUF1":
        raise ValueError("Invalid file format — missing signature")        

    use_rle = bool(data[4])
    use_delta = bool(data[5])
    offset = 6
    k = int.from_bytes(data[offset:offset+2], 'big')
    freq_table = {}
    offset += 2

    for i in range(k):
        symbol = data[offset]
        freq = int.from_bytes(data[offset + 1: offset + 9], 'big')
        freq_table[symbol] = freq
        offset += 9

    payload_offset = offset
    payload_bytes = data[payload_offset:]

    return freq_table, payload_offset, payload_bytes, True, use_rle, use_delta

# Algorithm for more compression

def delta_encode(data):
    if not data:
        return b""
    
    encoded = [data[0]]

    for i in range(1, len(data)):
        diff = (data[i] - data[i - 1]) % 256
        encoded.append(diff)
    
    return bytes(encoded)

def rle_encode(data):
    if not data:
        return b""
    
    encoded = []
    count = 1
    for i in range(1, len(data)):
        if data[i] == data[i - 1] and count < 255:
            count += 1

        else:
            encoded.append(data[i - 1])
            encoded.append(count)
            count = 1

    encoded.append(data[-1])
    encoded.append(count)

    return bytes(encoded)


def rle_decode(data):
    if data is None:
        return b''
    
    decoded = bytearray()
    i = 0
    while i < len(data):
        symbol = data[i]
        count = data[i + 1] if i + 1 < len(data) else 1
        decoded.extend([symbol] * count)
        i += 2
    return bytes(decoded)


def delta_decode(data):
    if not data:
        return b''
    
    decoded = [data[0]]

    for i in range(1, len(data)):
        value = (decoded[i - 1] + data[i]) % 256
        decoded.append(value)

    return bytes(decoded)

