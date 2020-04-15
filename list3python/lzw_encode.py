import sys
from math import log
BUFFER = 256


def encode_bin(num):
    encoded = []
    while num:
        encoded.append(num & 1)
        num = num >> 1
    encoded.reverse()
    return encoded


def memoize(f):
    memo = {}

    def wrapper(arg):
        if arg not in memo:
            memo[arg] = f(arg)
        return memo[arg]
    return wrapper


@memoize
def fibonacci(n):
    if n < 1:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-2) + fibonacci(n-1)


def encode_gamma(num):
    encoded = encode_bin(num)
    return [0 for _ in range(0, len(encoded)-1)] + encoded


def encode_delta(num):
    encoded = encode_bin(num)
    return [0 for _ in range(0, len(encode_bin(len(encode_bin(num))))-1)] + encode_bin(len(encoded)) + encoded[1:]


def encode_omega(num):
    encoded = [0]
    while num > 1:
        to_prepend = encode_bin(num)
        encoded = to_prepend + encoded
        num = len(to_prepend) - 1
    return encoded


def encode_fib(num):
    encoded = []
    while num:
        i = 2
        while fibonacci(i+1) <= num:
            i += 1
        if encoded:
            encoded[i-2] = 1
        else:
            encoded = [0 for _ in range(0, i-2)] + [1, 1]
        num -= fibonacci(i)
    return encoded



if len(sys.argv) >= 4 and sys.argv[3] == '-gamma':
    encoding_func = encode_gamma
elif len(sys.argv) >= 4 and sys.argv[3] == '-delta':
    encoding_func = encode_delta
elif len(sys.argv) >= 4 and sys.argv[3] == '-fibbo':
    encoding_func = encode_fib
else:
    encoding_func = encode_omega
symbols = {}
for i in range(0, 256):
    symbols[i] = [i + 1, {}]
next_index = 257
code = []
total_in_count = 0
total_out_count = 0
in_count = [0 for _ in range(0, 256)]
out_count = [0 for _ in range(0, 256)]
in_file = open(sys.argv[1], 'rb')
out_file = open(sys.argv[2], 'wb')
text = in_file.read(BUFFER)
while not text == b'':
    text_at = 0
    symbol = [None, symbols]
    while len(text) > text_at and symbol[1].get(text[text_at], None):
        symbol = symbol[1][text[text_at]]
        total_in_count += 1
        in_count[text[text_at]] += 1
        text_at += 1
        if len(text) == text_at:
            text += in_file.read(BUFFER)
    code += encoding_func(symbol[0])
    text = text[text_at:]
    if text:
        symbol[1][text[0]] = [next_index, {}]
        next_index += 1
    while len(code) >= 8:
        b = 0
        for i in range(0, 8):
            b = b << 1
            b += code.pop(0)
        total_out_count += 1
        out_count[b] += 1
        out_file.write(bytes([b]))
in_file.close()
if len(code):
    while len(code) < 8:
        if encoding_func == encode_omega:
            code.append(1)
        else:
            code.append(0)
    b = 0
    for i in range(0, 8):
        b = b << 1
        b += code.pop(0)
    total_out_count += 1
    out_count[b] += 1
    out_file.write(bytes([b]))
out_file.close()
print('Długość pliku wejściowego: ', total_in_count)
print('Długość pliku wyjściowego: ', total_out_count)
print('Stopień kompresji: ', total_in_count/total_out_count)
in_entropy = -sum(count/total_in_count * log(count/total_in_count, 256) for count in in_count if count > 0)
out_entropy = -sum(count/total_out_count * log(count/total_out_count, 256) for count in out_count if count > 0)
print('Entropia pliku wejściowego: ', in_entropy)
print('Entropia pliku wyjściowego: ', out_entropy)
