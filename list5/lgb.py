import sys
from math import log10
from struct import pack


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

        bitmap = [0] * (width*height)  
        for y in vert:
            for x in horiz:
                b = int.from_bytes(f.read(1), end)
                g = int.from_bytes(f.read(1), end)
                r = int.from_bytes(f.read(1), end)
                bitmap[y * width + x] = (r,g,b)
         
    return (width, height), bitmap

def avg_all_colors(bitmap):

    size = 1 if len(bitmap) == 0 else len(bitmap)
    ar,ag,ab = 0,0,0
    for b in bitmap:  
        ar += b[0] 
        ag += b[1] 
        ab += b[2] 

    return (ar//size, ag//size, ab//size)

def offset_color(color, eps):
    ro = max(min(color[0] + eps, 255), 0)
    go = max(min(color[1] + eps, 255), 0)
    bo = max(min(color[2] + eps, 255), 0)
    return (ro, go, bo)    


def avg_dists(codebook, bmap):
    all_dists = []
    for e in codebook:
        all_dists.append(get_dists(e, bmap))
    return all_dists


def split_codebook(codebook, bmap, all_dists_old, EPS):
    new_codebook = []
    for e in codebook:
        new_codebook.append(offset_color(e, 1)) 
        new_codebook.append(offset_color(e, -1))

    err = 255 + EPS

    while err > EPS:
        all_dists = avg_dists(new_codebook, bmap)

        clasters = [[] for _ in range(len(new_codebook))]
        d = []
        for i in range(len(bmap)):
            mi = all_dists[0][i]
            idx = 0
            for j in range(len(all_dists)):
                if all_dists[j][i] - mi < 0:
                    mi = all_dists[j][i]
                    idx = j
            clasters[idx].append(bmap[i])
            d.append(mi)

        new_codebook = []
        for c in clasters:
            new_codebook.append(avg_all_colors(c))

        new_dists = sum([c for c in d]) / len(clasters) 
        
        err = 0 if all_dists_old == 0 else (all_dists_old - new_dists) / all_dists_old
        all_dists_old = new_dists     

    return new_dists, new_codebook


def get_dists(c, bmap):
    dists = []
    for p in bmap:
        dists.append(norm(c, p))
    return dists


def norm(c0, c1):
    return abs(c0[0] - c1[0]) + abs(c0[1] - c1[1]) + abs(c0[2] - c1[2]) 


def genCodebook(size, bmap, no_color):
   
    avg_col = avg_all_colors(bmap)

    EPS = 1
    codebook = [avg_col] #offset_color(avg_col, -1), offset_color(avg_col, 1)]

    ado = get_dists(avg_col, bmap) 
    all_dists_old = sum(ado) / len(ado)

    while len(codebook) != no_color:
        all_dists_old, codebook = split_codebook(codebook, bmap, all_dists_old, EPS) 

    return codebook    


def findClosest(c, codebook):
    d = get_dists(c, codebook) 
    return d.index(min(d))


def genImage(codebook, bmap):
    img = []
    for e in bmap:
        img.append(codebook[findClosest(e, codebook)])

    return img


def save_tga(w, h, bitmap, file):
    with open(file, 'wb') as f:
        f.write(bytes([0]))
        f.write(bytes([0]))
        f.write(bytes([2]))

        f.write(pack('<H', 0))
        f.write(pack('<H', 0))
        f.write(bytes([0]))

        f.write(pack('<H', 0))
        f.write(pack('<H', 0))
        f.write(pack('<H', w))
        f.write(pack('<H', h))
        f.write(bytes([24]))
        f.write(bytes([32]))

        for r, g, b in bitmap:
            f.write(bytes([b]))
            f.write(bytes([g]))
            f.write(bytes([r]))

        for _ in range(26):
            f.write(bytes([0]))

def mse(old, new):
    mse_r = []
    for i in range(len(old)):
        mse_r.append(norm(old[i], new[i])**2)
    return sum(mse_r)/len(old)

def snr(mse_res, old):
    snr_r = []
    for i in range(len(old)):
        snr_r.append(norm(old[i], (0,0,0))**2)
    return (sum(snr_r)/len(old))/mse_res


s, bmap = read_tga(sys.argv[1])
mult = 2**int(sys.argv[3])
codebook = genCodebook(s, bmap, mult)
img = genImage(codebook, bmap)
mse_res = mse(bmap, img)
snr_r = snr(mse_res, bmap)
print("Błąd średniokwadratowy: ", mse_res)
print("Stosunek sygnału do szumu: ", snr_r, "(", 10*log10(snr_r),"dB )")
save_tga(s[0], s[1], img, sys.argv[2])