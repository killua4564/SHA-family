import numpy as np

RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
    0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
    0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]

W = 64      # W = 2 ** l
ROUND = 24  # ROUND = 12 + 2 * l
left_rotate = lambda n, b: (n << b | n >> (64 - b)) & 0xFFFFFFFFFFFFFFFF

def keccak1600(r, c, message):
    def theta(state):
        parity = np.zeros(5, dtype=np.uint64)
        for state_item in state.T:
            parity = parity ^ state_item
        state = state ^ np.roll(parity, 1, axis=0).reshape((5,1)) ^ left_rotate(np.roll(parity, 4, axis=0), 1).reshape((5,1))
        return state

    def rho(state):
        matrix = np.identity(2, dtype=np.uint8)
        base = np.array([[3, 2], [1, 0]], dtype=np.uint8)
        for t in range(24):
            j, i = matrix.dot([[0], [1]]).T[0]
            matrix = matrix.dot(base) % 5
            state[i][j] = left_rotate(int(state[i][j]), ((t+1) * (t+2) // 2) % 64)
        return state

    def pi(state):
        i, j = 1, 0
        current = state[i][j]
        for _ in range(24):
            i, j = j, (2 * i + 3 * j) % 5
            state[i][j], current = current, state[i][j]
        return state

    # def rho_pi(state):
    #     i, j = 1, 0
    #     current = state[i][j]
    #     for t in range(24):
    #         i, j = j, (2 * i + 3 * j) % 5
    #         state[i][j], current = left_rotate(int(current), ((t+1)*(t+2)//2)%64), state[i][j]
    #     return state

    def chi(state):
        state = state ^ (~np.roll(state, 4, axis=0) & np.roll(state, 3, axis=0))
        return state

    def iota(state, r):
        state[0][0] = int(state[0][0]) ^ RC[r]
        return state

    padding_length = r // 8 - len(message) % (r // 8)
    message += b"\x86" if padding_length == 1 else b"\x06" + bytes(padding_length - 2) +  b"\x80"
    message_list = list(map(lambda x: int.from_bytes(x, byteorder="little"), [message[i:i+8] for i in range(0, len(message), 8)]))

    state = np.zeros((5, 5), dtype=np.uint64)
    blocksize = 8 * r // W
    message_blocksize = blocksize // 8
    for i in range(0, len(message_list), message_blocksize):
        message_block = message_list[i:i+message_blocksize] + [0] * (25 - message_blocksize)
        state = state ^ np.array(message_block, dtype=np.uint64).reshape((5, 5)).T

        # main_loop
        for r in range(ROUND):
            state = iota(chi(pi(rho(theta(state)))), r)

    digest = b"".join(map(lambda x: int(x).to_bytes(8, byteorder="little"), state.T.reshape(25)))
    hexdigest = digest.hex()[:c // 8]
    return hexdigest

def hash224(message):
    return keccak1600(1152, 448, message)

def hash256(message):
    return keccak1600(1088, 512, message)

def hash384(message):
    return keccak1600(832, 768, message)

def hash512(message):
    return keccak1600(576, 1024, message)

message = b"The quick brown fox jumps over the lazy dog"
print(f"SHA3-224 {hash224(message)}")
print(f"SHA3-256 {hash256(message)}")
print(f"SHA3-384 {hash384(message)}")
print(f"SHA3-512 {hash512(message)}")

assert hash224(message) == "d15dadceaa4d5d7bb3b48f446421d542e08ad8887305e28d58335795"
assert hash256(message) == "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04"
assert hash384(message) == "7063465e08a93bce31cd89d2e3ca8f602498696e253592ed26f07bf7e703cf328581e1471a7ba7ab119b1a9ebdf8be41"
assert hash512(message) == "01dedd5de4ef14642445ba5f5b97c15e47b9ad931326e4b0727cd94cefc44fff23f07bf543139939b49128caf436dc1bdee54fcb24023a08d9403f9b4bf0d450"
