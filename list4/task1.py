import sys
from math import log2
from collections import Counter

def standards(A, B, C, s):

    def s1(NW, N, W):
        return W

    def s2(NW, N, W):
        return N

    def s3(NW, N, W):
        return NW

    def s4(NW, N, W):
        return N + W - NW

    def s5(NW, N, W):
        return N + (W - NW)//2

    def s6(NW, N, W):
        return W + (N - NW)//2

    def s7(NW, N, W):
        return (N + W)//2

    def s_new(NW, N, W):
        max_, min_ = max(N, W), min(N, W)
        if NW >= max_:
            return max_
        elif NW <= min_:
            return min_
        else:
            return W + N - NW

    return {'1': s1, '2': s2, '3': s3, '4': s4, '5': s5, '6': s6, '7': s7, 'new': s_new}[s](A, B, C)

def read_tga(fn):
    with open(fn, 'rb') as f:
        end = 'little' # endianness

        _ = int.from_bytes(f.read(1), end) # id_len
        _ = int.from_bytes(f.read(1), end) # col_map_type
        _ = int.from_bytes(f.read(1), end) # img_type
        
        # colormap
        _ = int.from_bytes(f.read(2), end) # first entry index
        _ = int.from_bytes(f.read(2), end) # colormap length
        _ = int.from_bytes(f.read(1), end) # colormap entry size

        # img info
        _ = int.from_bytes(f.read(2), end) # start x 
        _ = int.from_bytes(f.read(2), end) # start y
        width = int.from_bytes(f.read(2), end)
        height = int.from_bytes(f.read(2), end) 
        _ = int.from_bytes(f.read(1), end) # pixel depth

        img_descr = int.from_bytes(f.read(1), end)
        order = (img_descr & 0x00110000) >> 4

        if (order & 0x10) != 0:
            vert = range(height)
        else:
            vert = reversed(range(height))

        if (order & 0x01) == 0:
            horiz = range(width)
        else:
            horiz = reversed(range(width))

        bitmap = {}
        for y in vert:
            for x in horiz:
                b = int.from_bytes(f.read(1), end)
                g = int.from_bytes(f.read(1), end)
                r = int.from_bytes(f.read(1), end)
                bitmap[(y * width + x)] = (r, g, b)
                
    return (width, height), bitmap


# get pixels in N, W and NW from (x,y)
def get_NWNW(bmap, dims, x, y):
    if x == 0:
        NW = (0, 0, 0)
        W = (0, 0, 0)
        if y == 0:
            N = (0, 0, 0)
        else:
            N = bmap[(y-1) * dims[0]]
    elif y == 0:
        NW = (0, 0, 0)
        N = (0, 0, 0)
        W = bmap[x-1]
    else:
        N = bmap[(y-1)*dims[0] + x]
        W = bmap[y*dims[0] + x-1]
        NW = bmap[(y-1)*dims[0] + x-1]
    return NW, N, W


def jpeg(original, dims, option):
    res = []
    for y in range(dims[1]):
        for x in range(dims[0]):
            X = bmap[y * dims[0] + x]
            NW, N, W = get_NWNW(original, dims, x, y)
            # new rgb color pixel
            curr = ((X[0] - standards(NW[0], N[0], W[0], option)) % 256,
                    (X[1] - standards(NW[1], N[1], W[1], option)) % 256,
                    (X[2] - standards(NW[2], N[2], W[2], option)) % 256)
            res.append(curr)

    return res


def entropy(frequency, size):
    return -sum([(v/size)*(log2(v)-log2(size)) for v in frequency if v > 0])


def stat(new_bmap):
    size = len(new_bmap)
    full_ent = entropy(Counter(new_bmap).values(), size)
    r_ent = entropy(Counter([r for (r, _, _) in new_bmap]).values(), size)
    g_ent = entropy(Counter([g for (_, g, _) in new_bmap]).values(), size)
    b_ent = entropy(Counter([b for (_, _, b) in new_bmap]).values(), size)

    print('---------------------------------------')
    print(f'global entropy: {full_ent}')
    print(f'red entropy: {r_ent}')
    print(f'green entropy: {g_ent}')
    print(f'blue entropy: {b_ent}')
    print('---------------------------------------')
    return ((full_ent,o), (r_ent,o), (g_ent,o), (b_ent,o))


fn = sys.argv[1]
spec, bmap = read_tga(fn)
ops = ['1','2','3','4','5','6','7','new']

results = []
print(f'Stats for file: {fn}')
print()
for o in ops:
    res =jpeg(bmap, spec, o)
    print(f'Standard: {o}')
    r = stat(res)
    print()
    results.append(r)

print('Best standard for:')
w = min([x[0] for x in results], key = lambda t: t[0])
print(f'whole file:\tstandard\t{w[1]}\t({w[0]})')
r = min([x[1] for x in results], key = lambda t: t[0])
print(f'red color:\tstandard\t{r[1]}\t({r[0]})')
g = min([x[2] for x in results], key = lambda t: t[0])
print(f'green color:\tstandard\t{g[1]}\t({g[0]})')
b = min([x[3] for x in results], key = lambda t: t[0])
print(f'blue color:\tstandard\t{b[1]}\t({b[0]})')
