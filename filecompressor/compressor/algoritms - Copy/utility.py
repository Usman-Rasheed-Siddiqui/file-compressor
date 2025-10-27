import os

# read_binary_files(path)
# write_binary_files(path, data)
# get_file_size(path)
#bitstring_to_bytes(bitstring)
#byte_to_bitstring(data)


def read_binary_file(path):
    try:
        with open(f"{path}", "rb") as file:
            byte = file.read()
    
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
        return b''

    except Exception as e:
        print(f"[ERROR] Failed to read file {path}: {e}")
        return b''

    return byte

def write_binary_file(path, data):

    with open(f"{path}", "wb") as file:
        file.write(data)
        file.flush()
    
    return True

def get_file_size(path):

    try:
        if os.path.exists:
            file_info = os.stat(path)
            size_in_bytes = file_info.st_size
    
    except FileExistsError:
        print(f"File with path {path} does not exist")

    return size_in_bytes

def format_size(size_in_bytes):
    try:
        if not isinstance(size_in_bytes, (bytes, bytearray, memoryview)):
            raise TypeError("Data must be byte-like.")
        
        if size_in_bytes < 1024:
            return f"{size_in_bytes} bytes"
        elif size_in_bytes < 1024 ** 2:
            return f"{size_in_bytes / 1024:.2f} KB"
        elif size_in_bytes < 1024 ** 3:
            return f"{size_in_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_in_bytes / (1024 ** 3):.2f} GB"

    except ValueError:
        print("Invalid input for bytes")


def build_frequency_table(data: bytes):
    
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("Data must be byte-like.")

    frequency_count = {}
    for byte in data:
        if not isinstance(byte, int) or not (0 <= byte <= 255):
            print("[DEBUG] Invalid byte found in data:", byte)

        if byte not in frequency_count:
            frequency_count[byte] = 1
        else:
            frequency_count[byte] += 1
    
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
        raise TypeError( "Bitstring not a multiple of 8")

    count = 0
    string_to_bytes = []
    chunk = ""

    for bit in bitstring:
        count += 1
        chunk += bit 
        if count == 8:
            count = 0
            chunk = int(chunk, 2)
            string_to_bytes.append(chunk)
            chunk = ""

    return bytes(string_to_bytes)


def pad_bitstring(bitstring):
    pad_len = (8-(len(bitstring) % 8)) % 8

    padded_bitstring = bitstring + (pad_len * "0")
    header = format(pad_len, '08b')         # Converting pad_len to it's 8 bit binary form

    full_bitstring = header + padded_bitstring

    return full_bitstring    


def remove_padding(padded_bitstring):
    
    if isinstance(padded_bitstring, bytes):
        # Convert bytes to bitstring
        padded_bitstring = ''.join(f"{byte:08b}" for byte in padded_bitstring)
    
    if len(padded_bitstring) < 8:
        raise TypeError("Corrupted File - bitstream too short")

    pad_len = int(padded_bitstring[:8], 2)
    if pad_len > 0:
        cleaned_bitstring = padded_bitstring[8: -pad_len]
    else:
        cleaned_bitstring = padded_bitstring[8:]


    return cleaned_bitstring


def save_frequency_table(path, freq_table, payload_bytes):
    header = bytearray()
    header += b"HUF1"

    if not isinstance(freq_table, dict) or len(freq_table) == 0:
        raise ValueError("Incorrect Inputs: freq_table empty or not a dict")
    
    k = len(freq_table)
    if not (1 <= k <= 256):
        raise ValueError(f"Invalid number of symbols in freq_table: {k}")
    
    header += k.to_bytes(2, 'big')

    for symbol, freq in freq_table.items():
        if not isinstance(symbol, int):
            raise TypeError(f"Symbol {symbol} must be an integer")
        if not (0 <= symbol <= 255):
            raise ValueError(f"Invalid symbol {symbol} — must be between 0 and 255")
        
        if not isinstance(freq, int) or freq < 0:
            raise ValueError(f"Invalid frequency for symbol {symbol}")


        header += bytes([symbol])
        header += freq.to_bytes(8, 'big')

    output_data = header + payload_bytes
    write_binary_file(path, output_data)

    return {'path': path, 'header_len': len(header), 'payload_len': len(payload_bytes)}


def calculate_compression_ratio(original_size, compressed_size):
    if not isinstance(original_size, (int, float)) or not isinstance(compressed_size, (int, float)):
        raise TypeError("Sizes must be numeric values.")
    if original_size <= 0:
        return 0.0
    
    print(f"[DEBUG] Original Size: {original_size}")
    print(f"[DEBUG] Compressed Size: {compressed_size}")

    ratio = (1 - compressed_size / original_size) * 100
    # ratio = ((original_size - compressed_size) / original_size) * 100
    return round(ratio, 2)


def load_frequency_table(path):
    
    BASE_DIR = os.path.dirname(__file__)  # folder of this script
    path = os.path.join(BASE_DIR, path)

    with open(path, 'rb') as file:
        data = file.read()
    
    if len(data) < 6:
        raise ValueError("File too short to be a valid HUF file")

    signature = data[:4]
    if signature != b"HUF1":
        raise ValueError("Invalid file format — missing signature")        

    k = int.from_bytes(data[4:6], 'big')

    if k == 0:
        raise ValueError("Frequency table count k is zero — file is invalid or corrupted")
    if k > 256:
        raise ValueError(f"Invalid symbol count k={k} (too large) — file corrupted")

    expected_header_len = 6 + k * 9  # each symbol: 1 byte symbol + 8 byte freq
    if len(data) < expected_header_len:
        raise ValueError(f"File too short for expected frequency table (need >= {expected_header_len} bytes).")

    freq_table = {}
    offset = 6
    for i in range(k):
        symbol = data[offset]
        freq = int.from_bytes(data[offset + 1: offset + 9], 'big')
        freq_table[symbol] = freq
        offset += 9

    payload_offset = offset
    payload_bytes = data[payload_offset:]

    if len(payload_bytes) == 0:
        print("[WARNING] Payload bytes length is 0 — there is no compressed payload.")

    return freq_table, payload_offset, payload_bytes

# Algorithm for more compression

def delta_encode(data):
    if not data:
        return b""
    
    encoded = []
    encoded.append(data[0])

    for i in range(1, len(data)):
        diff = data[i] - data[i - 1]
        if diff < 0:
            diff = (diff + 256) % 256
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

    for i in range(0, len(data), 2):
        symbol = data[i]
        count = data[i + 1]
        decoded += bytes([symbol]) *count
    
    return bytes(decoded)


def delta_decode(data):
    if data is None:
        return b''
    
    decoded = []
    decoded.append(data[0])

    for i in range(1, len(data)):
        value = (decoded[i - 1] + data[i]) % 256
        decoded.append(value)

    return bytes(decoded)



# New
def adaptive_rle(data: bytes, min_run=3) -> bytes:
    """RLE that compresses long runs only when beneficial."""
    encoded = rle_encode(data)
    if len(encoded) < len(data) * 0.95:
        print("[INFO] RLE applied")
        return encoded
    else:
        print("[INFO] RLE skipped (not efficient)")
        return data
