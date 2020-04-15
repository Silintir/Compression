import bitarray
import sys
import getopt
from math import log2

# consts
HIGH = 65535 # max uint16
HALF = 32768 # 0.50 max uint16
H_QUARTER = 49152 # 0.75 max uint16
L_QUARTER = 16384 # 0.25 max uint16


def create_freq_tab():
    return [x for x in range(258)]


def f_get(freq, c):
    ci = int.from_bytes(c, byteorder='big')
    ret = (freq[ci], freq[ci+1], freq[257])

    if freq[257] < L_QUARTER:
        for i in range(ci + 1, len(freq)):
            freq[i] += 1

    return ret


def f_char(freq, num):
    for i in range(len(freq)-1):
        if num < freq[i+1]:
            return i
    else:
        return 256


def encode_char(freqs, c):
    global low
    global high
    global counter
    result = ''
    p = f_get(freqs, c)
    d = high - low + 1
    high = low + (d*p[1]) // p[2] - 1
    low += (d * p[0]) // p[2]

    while 1:
        if high < HALF:
            low *= 2
            high = (high * 2) + 1

            result += '0' + '1'*counter

            counter = 0
        elif low >= HALF:
            low = (low - HALF) * 2
            high = ((high - HALF) * 2) + 1
            result += '1' + '0'*counter
            counter = 0
        elif low >= L_QUARTER and high < H_QUARTER:
            low = (low - L_QUARTER) * 2
            high = ((high - L_QUARTER) * 2) + 1
            counter += 1
        else:
            break
    return result


def encode(text):
    freqs = create_freq_tab()
    global low
    global high
    global counter
    low = 0
    high = HIGH
    counter = 0

    result = []

    for b in text:
        result.append(encode_char(freqs, b))

    result.append(encode_char(freqs, b'\x01\x00'))

    counter += 1

    if low <= L_QUARTER:
        result.append('0' + '1'*counter)
    else:
        result.append('1' + '0'*counter)
    return result


def decode(code):
    freqs = create_freq_tab()
    low = 0
    high = HIGH
    res = 0
    text = []
    i = 0

    for _ in range(16):
        res = (res << 1) | int(code[i])
        i += 1

    while 1:
        d = high - low + 1
        val = ((res - low + 1) * freqs[257] - 1) // d
        c = f_char(freqs, val)
        

        if c == 256:
            break
        else:
            text.append(c)

        p = f_get(freqs, c.to_bytes(2, 'big'))
        high = low + (p[1] * d) // p[2] - 1
        low += (d * p[0]) // p[2]

        while 1:
            if high < HALF:
                low *= 2
                high = (high*2) + 1
                try:
                    res = (res * 2) + int(code[i])
                except IndexError:
                    res = (res * 2)

            elif low >= HALF:
                low = (low - HALF) * 2
                high = ((high - HALF) * 2) + 1
                try:
                    res = ((res - HALF) * 2) + int(code[i])
                except IndexError:
                    res = ((res - HALF) * 2)

            elif low >= L_QUARTER and high < H_QUARTER:
                low = (low - L_QUARTER) * 2
                high = ((high - L_QUARTER) * 2) + 1
                try:
                    res = ((res - L_QUARTER) * 2) + int(code[i])
                except IndexError:
                    res = ((res - L_QUARTER) * 2)

            else:
                break
            i += 1
    return bytes(text)


def entropy(text):
    f = {}
    size = len(text)
    for c in text:
        if c in f:
            f[c] += 1
        else:
            f[c] = 1
    return -sum([(v/size)*(log2(v)-log2(size))
                 for v in f.values() if v > 0])


def stats(text, code):
    print('Entropia oryginalnego tekstu: ', entropy(text))
    x = [len(c) for c in code]
    avg = sum(x)/len(x)
    print('Średnia długość kodowania: ', avg)
    cr = 8*len(text)/len(''.join(code))
    print('Stopień kompresji: ', cr)



opts, _ = getopt.gnu_getopt(sys.argv[1:], 'edi:o:')
encoding = True
for opt, arg in opts:
    if opt == '-i':
        file_in = arg
    elif opt == '-o':
        file_out = arg
    elif opt == '-d':
        encoding = False


ba = bitarray.bitarray()
if encoding:
    chars = []

    with open(file_in, "rb") as f:
        while byte:= f.read(1):
            chars.append(byte)

    code = encode(chars)
    ba.extend(''.join(code))
    file_w = open(file_out,mode='wb')
    ba.tofile(file_w)
    stats(chars, code)
else:
    file = open(file_in,mode='rb')
    all_of_it = file.read()
    file.close()

    ba.frombytes(all_of_it)
    bits = ba.to01()
    byte_text = decode(bits)
    
    file_w = open(file_out, 'wb')
    file_w.write(byte_text)
    file_w.close()
        


