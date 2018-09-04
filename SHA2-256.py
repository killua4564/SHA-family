message = b"The quick brown fox jumps over the lazy dog"
message_length = len(message) * 8
right_rotate = lambda n, b: ((n >> b) | (n << (32 - b))) & 0xffffffff

# initialization variables
h0 = 0x6a09e667
h1 = 0xbb67ae85
h2 = 0x3c6ef372
h3 = 0xa54ff53a
h4 = 0x510e527f
h5 = 0x9b05688c
h6 = 0x1f83d9ab
h7 = 0x5be0cd19

# initialize table of round constants
k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

# pre-processing
message += b"\x80"
message += b"\x00" * ((56 - len(message) % 64) % 64)
message += message_length.to_bytes(8, byteorder="big")

# break the message in 512bits chunks
chunks = [message[i:i+64] for i in range(0, len(message), 64)]
for chunk in chunks:
    # break chuck into sixteen 32bits big-endian words
    w = [int.from_bytes(chunk[i:i+4], byteorder="big") for i in range(0, len(chunk), 4)]
    # extend 16 words to 64 words
    for i in range(16, 64):
        s0 = right_rotate(w[i-15], 7) ^ right_rotate(w[i-15], 18) ^ (w[i-15] >> 3)  # right_rotate(w[i-15], 3)
        s1 = right_rotate(w[i-2], 17) ^ right_rotate(w[i-2], 19) ^ (w[i-2] >> 10)   # right_rotate(w[i-2], 10)
        w.append((w[i-16] + s0 + w[i-7] + s1) & 0xffffffff)

    # initialize hash value for this chunk
    a = h0
    b = h1
    c = h2
    d = h3
    e = h4
    f = h5
    g = h6
    h = h7

    # main loop
    for i in range(64):
        s0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
        s1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
        choice = (e & f) ^ (~e & g)
        majority = (a & b) ^ (a & c) ^ (b & c)
        temp1 = (h + s1 + choice + k[i] + w[i]) & 0xffffffff
        temp2 = (s0 + majority) & 0xffffffff
        
        a, b, c, d, e, f, g, h = (temp1 + temp2) & 0xffffffff, a, b, c, (d + temp1) & 0xffffffff, e, f, g

    # add this chunk's hash to result so far
    h0 = (h0 + a) & 0xffffffff
    h1 = (h1 + b) & 0xffffffff
    h2 = (h2 + c) & 0xffffffff
    h3 = (h3 + d) & 0xffffffff
    h4 = (h4 + e) & 0xffffffff
    h5 = (h5 + f) & 0xffffffff
    h6 = (h6 + g) & 0xffffffff
    h7 = (h7 + h) & 0xffffffff

# produce the final hash value
digest = "".join(map(lambda x: x.to_bytes(4, byteorder="big").hex(), (h0, h1, h2, h3, h4, h5, h6, h7)))
print(digest)

assert digest == "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
