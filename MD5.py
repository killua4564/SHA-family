# define message and function
message = b"The quick brown fox jumps over the lazy dog"
message_length = len(message) * 8
left_rotate = lambda n, b: ((n << b) | (n >> (32 - b))) & 0xffffffff

# initialization variables
h0 = 0x67452301
h1 = 0xefcdab89
h2 = 0x98badcfe
h3 = 0x10325476

# initialize table of round constants
k = [
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
]

r = [
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
]

# pre-processing
message += b"\x80"
message += b"\x00" * ((56 - len(message) % 64) % 64)
message += message_length.to_bytes(8, byteorder="little")

# break the message in 512bits chunks
chunks = [message[i:i+64] for i in range(0, len(message), 64)]
for chunk in chunks:
    # break chuck into sixteen 32bits little-endian words
    w = [int.from_bytes(chunk[i:i+4], byteorder="little") for i in range(0, len(chunk), 4)]

    # initialize hash value for this chunk
    a = h0
    b = h1
    c = h2
    d = h3

    # main loop
    for i in range(64):
        if 0 <= i <= 15:
            f = (b & c) | (~b & d)
            g = i
        elif 16 <= i <= 31:
            f = (b & d) | (c & ~d)
            g = (5 * i + 1) % 16
        elif 32 <= i <= 47:
            f = b ^ c ^ d
            g = (3 * i + 5) % 16
        elif 48 <= i <= 63:
            f = c ^ (b | ~d)
            g = (7 * i) % 16
        
        a, b, c, d = d, (left_rotate((a + f + k[i] + w[g]) & 0xffffffff, r[i]) + b) & 0xffffffff, b, c

    # add this chunk's hash to result so far
    h0 = (h0 + a) & 0xffffffff
    h1 = (h1 + b) & 0xffffffff
    h2 = (h2 + c) & 0xffffffff
    h3 = (h3 + d) & 0xffffffff

# produce the final hash value
digest = "".join(map(lambda x: x.to_bytes(4, byteorder="little").hex(), (h0, h1, h2, h3)))
print(digest)

assert digest == "9e107d9d372bb6826bd81d3542a419d6"
