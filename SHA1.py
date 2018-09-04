# define message and function
message = b"The quick brown fox jumps over the lazy dog"
message_length = len(message) * 8
left_rotate = lambda n, b: ((n << b) | (n >> (32 - b))) & 0xffffffff

# initialization variables
h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0

# pre-processing
message += b"\x80"
message += b"\x00" * ((56 - len(message) % 64) % 64)
message += message_length.to_bytes(8, byteorder="big")

# break the message in 512bits chunks
chunks = [message[i:i+64] for i in range(0, len(message), 64)]
for chunk in chunks:
    # break chuck into sixteen 32bits big-endian words
    w = [int.from_bytes(chunk[i:i+4], byteorder="big") for i in range(0, len(chunk), 4)]
    # extend 16 words to 80 words
    for i in range(16, 80):
        w.append(left_rotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1))
    
    # initialize hash value for this chunk
    a = h0
    b = h1
    c = h2
    d = h3
    e = h4

    # main loop
    for i in range(80):
        if 0 <= i <= 19:
            f = (b & c) | (~b & d)
            k = 0x5A827999
        elif 20 <= i <= 39:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif 40 <= i <= 59:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        elif 60 <= i <= 79:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        a, b, c, d, e = (left_rotate(a, 5) + f + e + k + w[i]) & 0xffffffff, a, left_rotate(b, 30), c, d

    # add this chunk's hash to result so far
    h0 = (h0 + a) & 0xffffffff
    h1 = (h1 + b) & 0xffffffff
    h2 = (h2 + c) & 0xffffffff
    h3 = (h3 + d) & 0xffffffff
    h4 = (h4 + e) & 0xffffffff

# produce the final hash value
digest = "".join(map(lambda x: x.to_bytes(4, byteorder="big").hex(), (h0, h1, h2, h3, h4)))
print(digest)

assert digest == "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
