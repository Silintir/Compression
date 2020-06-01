
def get_avg_col(bitmap):
    size = 1 if len(bitmap) == 0 else len(bitmap)
    a = int(sum([b for b in bitmap]) / size) 
    return a


def avg_dists(cb, bmap):
    all_dists = []
    for e in cb:
        all_dists.append(get_dists(e, bmap))
    return all_dists


def split_codebook(cb, bmap, all_dists_old, EPS):
    ncb = []
    for e in cb:
        ncb.append(e + 1)
        ncb.append(e - 1)

    # initial error
    err = 255 + EPS

    while err > EPS:
        all_dists = avg_dists(ncb, bmap)

        closers = [[] for _ in range(len(ncb))]
        d = []
        for i in range(len(bmap)):
            mi = all_dists[0][i]
            idx = 0
            for j in range(len(all_dists)):
                if all_dists[j][i] - mi < 0:
                    mi = all_dists[j][i]
                    idx = j
            closers[idx].append(bmap[i])
            d.append(mi)

        ncb = []
        for c in closers:
            ncb.append(get_avg_col(c))

        new_dists = sum([c for c in d]) / len(closers) 
        
        err = (all_dists_old - new_dists) / all_dists_old if all_dists_old > 0 else 0
        all_dists_old = new_dists     

    return new_dists, ncb


def get_dists(c, bmap):
    dists = []
    for p in bmap:
        dists.append(norm(c, p))
    return dists


def norm(c0, c1):
    return abs(c0 - c1)


def genCodebook(bmap, no_color):

    avg_col = get_avg_col(bmap)

    EPS = 1
    codebook = [avg_col] 

    ado = get_dists(avg_col, bmap) 
    all_dists_old = sum(ado) / len(ado)

    while len(codebook) != no_color:
        all_dists_old, codebook = split_codebook(codebook, bmap, all_dists_old, EPS) 

    return codebook    


def findClosest(c, cb):
    d = get_dists(c, cb) 
    return d.index(min(d))


def save_quant(cb, bmap):
    quant = []
    for i in bmap:
        quant.append(findClosest(i, cb))
    return quant


def load_quant(cb, bmap):
    img = []
    for e in bmap:
        img.append(cb[e])
    return img
