import sys
from struct import pack
import lbg
from bitarray import bitarray

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
        order = (img_descr & 0b00110000) >> 4

        if (order & 0b10) != 0:
            vert = range(height)
        else:
            vert = reversed(range(height))

        if (order & 0b01) == 0:
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


def norm(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])    


def square_mis(old_img, new_img, f):
    mis = []
    for i in range(len(old_img)):
        mis.append(f(old_img[i], new_img[i])**2)

    return sum(mis) / len(mis)    


def get_snr(img, mse):
    return sum([sum(pix)**2 for pix in img])/len(img)/mse


def offset_color(color):
    ro = max(min(color[0], 255), 0)
    go = max(min(color[1], 255), 0)
    bo = max(min(color[2], 255), 0)
    return (ro, go, bo)  


def diff_encoding(bitmap):
    prev = (0,0,0)
    encoded = [0] * len(bitmap)
    for num, pixel in enumerate(bitmap):
        encoded[num] = (pixel[0]-prev[0], pixel[1]-prev[1], pixel[2]-prev[2])
        prev = pixel

    return encoded


def diff_decoding(bitmap):
    prev = (0,0,0)
    decoded = [0] * len(bitmap)
    for num, pixel in enumerate(bitmap):
        decoded[num] = (pixel[0]+prev[0], pixel[1]+prev[1], pixel[2]+prev[2])
        prev = decoded[num]

    return decoded 


def filter_image(bitmap):
    lo = [(0,0,0)] * (len(bitmap)//2)
    hi = [(0,0,0)] * (len(bitmap)//2)

    for i in range(len(bitmap)//2):
        x1 = bitmap[i*2]
        x2 = bitmap[(i*2)+1]

        y2 = ( (x1[0] + x2[0]) // 2, (x1[1] + x2[1]) // 2, (x1[2] + x2[2]) // 2 )
        z2 = ( (x2[0] - y2[0]), (x2[1] - y2[1]), (x2[2] - y2[2]) )
        lo[i] = y2
        hi[i] = z2

    return lo, hi


def unfilter_image(lo, hi):
    res = []
    for l, u in zip(lo, hi):
        x2 = (u[0] + l[0]), (u[1] + l[1]), (u[2] + l[2])
        x1 = (2*l[0] - x2[0]), (2*l[1] - x2[1]), (2*l[2] - x2[2])
        res.append(offset_color(x1))
        res.append(offset_color(x2))

    return res


def compress_upper(bmap, lvls):
    r = [x[0] for x in bmap]
    g = [x[1] for x in bmap]
    b = [x[2] for x in bmap]
    
    rc = lbg.genCodebook(r, 2**lvls)
    gc = lbg.genCodebook(g, 2**lvls)
    bc = lbg.genCodebook(b, 2**lvls)

    r_img = lbg.save_quant(rc, r)
    g_img = lbg.save_quant(gc, g)
    b_img = lbg.save_quant(bc, b)

    return (r_img, g_img, b_img), (rc, gc, bc)


def compress_lower(lo, lvls):
    lo = [[x[0], x[1], x[2]] for x in lo]
    re_bmap = diff_encoding(lo)
    r = [x[0] for x in re_bmap]
    g = [x[1] for x in re_bmap]
    b = [x[2] for x in re_bmap]
   
    rc = lbg.genCodebook(r, 2**lvls)
    gc = lbg.genCodebook(g, 2**lvls)
    bc = lbg.genCodebook(b, 2**lvls)

    closers_r = lbg.save_quant(rc, r)
    closers_g = lbg.save_quant(gc, g)
    closers_b = lbg.save_quant(bc, b)

    re_bmap = diff_decoding(re_bmap)
    re_bmap = [[x[0], x[1], x[2]] for x in re_bmap]

    for i in range(1, len(lo)):
        lo[i][0] -= re_bmap[i-1][0]
        lo[i][1] -= re_bmap[i-1][1]
        lo[i][2] -= re_bmap[i-1][2]

        closers_r[i] = lbg.findClosest(lo[i][0], rc)
        closers_g[i] = lbg.findClosest(lo[i][1], gc)
        closers_b[i] = lbg.findClosest(lo[i][2], bc)
       
        if i > 1:
            last = [re_bmap[i-2][0], re_bmap[i-2][1], re_bmap[i-2][2]]
        else:
            last = [0,0,0] 
 
        for j in range(i-1, len(re_bmap)):
            last[0] += rc[closers_r[j]]
            last[1] += gc[closers_g[j]]
            last[2] += bc[closers_b[j]]
            re_bmap[j][0] = last[0]
            re_bmap[j][1] = last[1]
            re_bmap[j][2] = last[2]

    # return fixed idxs
    return (closers_r, closers_g, closers_b), (rc, gc, bc)


def dequantize(cbs, bmaps):
    rc, gc, bc = cbs
    rq, gq, bq = bmaps
    
    r = lbg.load_quant(rc, rq)
    g = lbg.load_quant(gc, gq)
    b = lbg.load_quant(bc, bq)

    return list(zip(r, g, b))


def main():
        if sys.argv[1] in ('-e', '--encode'):
            
            in_file = sys.argv[2]
           
            try:
                k = int(sys.argv[4])
            except ValueError:
                print(sys.argv[4], " is not a integer")
                return
            
            if k < 1 or k > 7:
                print(k, " is not in allowed range")
                return
            
            size, bmap = read_tga(in_file)
            l, u = filter_image(bmap)

            lbmaps, cl = compress_lower(l, k)
            ubmaps, cu = compress_upper(u, k)

            out = bitarray(endian='little')
            out.frombytes(pack('<H', size[0]))
            out.frombytes(pack('<H', size[1]))
            out.frombytes(pack('<H', k))
            
            def make_short(c):
                    if c < 0:
                        out.extend([True])
                        c *= -1
                        out.frombytes(bytes([c]))
                    else:
                        out.extend([False])
                        out.frombytes(bytes([c]))
            
            
            def save_from_kbits(num):
                
                for i in range(k-1,-1,-1):
                    comp = 2 ** i
                    if num & comp == comp:
                        out.extend([True])
                    else:
                        out.extend([False])

            
            for i in cl:
                for j in i:
                    make_short(j) 
            for i in cu:
                for j in i:
                    make_short(j) 
            for cbk in lbmaps:
                for j in cbk:
                    save_from_kbits(j)
            for cbk in ubmaps:
                for j in cbk:
                    save_from_kbits(j)
            

            out_file = open(sys.argv[3], "wb")

            out.tofile(out_file)
            out_file.close()

        elif sys.argv[1] in ('-d', '--decode'):

            in_file = sys.argv[2]
            out_file = sys.argv[3]

            end = 'little'

            with open(in_file, 'rb') as f:
                width = int.from_bytes(f.read(2), end)
                height = int.from_bytes(f.read(2), end)
                k = int.from_bytes(f.read(2), end)

                out = bitarray(endian=end)
                out.frombytes(f.read())
                

            def get_cbks(out):
                it = 0
                cla, cl = [0] * 3, [0] * 2**k
                for i in range(3):
                    for j in range(2**k):

                        temp = out[it+1:it+9]
                        cl[j] = int.from_bytes(temp.tobytes(), end)

                        if out[it] == 1:
                            cl[j] *= (-1)

                        it += 9
                    cla[i] = cl

                    cl = [0] * 2**k
                # 3 times, 9 bits long = 27
                return cla, out[27*(2**k):]
            
            cl, out = get_cbks(out)
            cu, out = get_cbks(out)

            def get_bmaps(out):

                itt = 0
                bmap, b = [0] * 3, [0] * ((width*height) // 2)

                for i in range(3): 
                    for j in range( (width*height) // 2 ):
                        s_v = 0
                        for z in range(k-1,-1,-1):
                            s_v += 2**z if out[itt] == 1 else 0
                            itt += 1
                        b[j] = s_v
                    bmap[i] = b
                    b = [0] * ((width*height) // 2)

                return bmap, out[(3*k*(width*height) // 2):]

            
            lbmaps, out = get_bmaps(out)
            ubmaps, out = get_bmaps(out)

            ll = dequantize(cl, lbmaps)
            uu = dequantize(cu, ubmaps)

            lll = diff_decoding(ll)
            img = unfilter_image(lll, uu)

            save_tga(width, height, img, out_file)

        elif sys.argv[1] in ('-s', '--stats'):

            _, bmap = read_tga(sys.argv[2])
            _, img = read_tga(sys.argv[3])
            
            bmap_r = [x[0] for x in bmap]
            bmap_g = [x[1] for x in bmap]
            bmap_b = [x[2] for x in bmap]

            img_r = [x[0] for x in img]
            img_g = [x[1] for x in img]
            img_b = [x[2] for x in img]

            sm = square_mis(bmap, img, norm)
            sm_r = square_mis(bmap_r, img_r, lbg.norm)
            sm_g = square_mis(bmap_g, img_g, lbg.norm)
            sm_b = square_mis(bmap_b, img_b, lbg.norm)

            print('RGB MSE: ', sm)
            print('MSE r: ', sm_r)
            print('MSE g: ', sm_g)
            print('MSE b: ', sm_b)
            print('SNR: ',get_snr(bmap, sm))
            

 
if __name__ == '__main__':
    main()