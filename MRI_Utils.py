#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#get_ipython().run_line_magic('matplotlib', 'inline')
# import matplotlib.pyplot as plt
import numpy as np


# In[ ]:
def normalize_data(k): #杈撳叆k涓簄umpy鐨勪簩缁寸煩闃碉紝杩斿洖鍊间负缂╂斁鍦�0-x鐨勪簩缁寸煩闃�
    norm_arr = ((k - k.min()) * ((1/(k.max() - k.min())) * 1024)) #鍥惧儚鏁版嵁褰掍竴鍖栵紝灏嗙煩闃典腑鐨勬渶灏忓€肩缉鏀惧埌0锛屾渶澶у€间负1024
    return norm_arr

def Read_XMD(path):
#     binFile = open(path,'rb')
    with open(path,'rb') as binFile:
        b_offset = binFile.read(4)
        offset = np.frombuffer(b_offset,dtype=np.int32)[0]
        # print('offset=',offset)

        b_samples = binFile.read(4)
        samples = np.frombuffer(b_samples,dtype=np.int32)[0]
        # print('sampels=',samples)

        b_Views = binFile.read(4)
        Views = np.frombuffer(b_Views,dtype=np.int32)[0]
        # print('Views=',Views)

        b_Views2 = binFile.read(4)
        Views2 = np.frombuffer(b_Views2,dtype=np.int32)[0]
        # print('Views2=',Views2)

        b_Slices = binFile.read(4)
        Slices = np.frombuffer(b_Slices,dtype=np.int32)[0]
        # print('Slices=',Slices)

        b_Echoes = binFile.read(4)
        Echoes = np.frombuffer(b_Echoes,dtype=np.int32)[0]
        # print('Echoes=',Echoes)

        b_Experiments = binFile.read(4)
        Experiments = np.frombuffer(b_Experiments,dtype=np.int32)[0]
        # print('Experiments=',Experiments)

        b_Nex = binFile.read(4)
        Nex = np.frombuffer(b_Nex,dtype=np.int32)[0]
        # print('Nex=',Nex)

        b_Chennels = binFile.read(4)
        Chennels = np.frombuffer(b_Chennels,dtype=np.int32)[0]
        # print('Channels=',Chennels)
        datasize = samples*Views*Views2*Slices*Echoes*Experiments*2
        # print('datasize=',datasize)
#     binFile.close()
    return offset,samples,Views,Views2,Slices,Echoes,Experiments,Nex,Chennels,datasize
def Read_MRD(mrd_file):
#     binFile = open(path,'rb')
    with open(mrd_file, 'rb') as xmd:
        xmd_lines = xmd.readlines()
        for seq in xmd_lines:
            seq = str(seq)
            if 'views_per_seg' in seq:
                seq1 = seq.split((','))
                etl = int((seq1[1].split('\\'))[0])
                print('etl=', etl)
    with open(mrd_file,'rb') as binFile:
        # binFile.seek(0,0)

        b_samples = binFile.read(4)
        samples, = np.frombuffer(b_samples, dtype=np.int32)
        print('sampels=', samples)
        # print(binFile.tell())
        b_Views = binFile.read(4)
        Views = np.frombuffer(b_Views, dtype=np.int32)[0]
        print('Views=', Views)

        b_Views2 = binFile.read(4)
        Views2 = np.frombuffer(b_Views2, dtype=np.int32)[0]
        print('Views2=', Views2)

        b_Slices = binFile.read(4)
        Slices = np.frombuffer(b_Slices, dtype=np.int32)[0]
        print('Slices=', Slices)

        binFile.seek(152,0)
        b_Echoes = binFile.read(4)
        Echoes = np.frombuffer(b_Slices, dtype=np.int32)[0]
        print('Echoes=', Echoes)

        b_Experiment = binFile.read(4)
        Experiment = np.frombuffer(b_Experiment, dtype=np.int32)[0]
        print('Experiment=',Experiment)
        Slices = Slices*Views2
        with open (mrd_file,'rb') as xmd:
            xmd_lines = xmd.readlines()
            for seq in xmd_lines:
                seq = str(seq)
                if 'views_per_seg' in seq:
                    seq1 = seq.split((','))
                    etl = int((seq1[1].split('\\'))[0])
                    print('etl=',etl)

        raw_list = []
        for i in range(0, Slices*Views*samples*8, 4):
            binFile.seek(512 + i, 0)
            b_raw = binFile.read(4)
            raw = np.frombuffer(b_raw, dtype=np.float32)[0]
            raw_list.append(raw)
        print('len=',len(raw_list))
        real = raw_list[::2]
        real1 = np.array(real)
        img = raw_list[1::2]
        img1 = np.array(img) * 1j
        cplx = real1 + img1
        s = []
        for o in range(0, len(cplx), samples * Views):
            b = cplx[o:o + samples * Views]
            s.append(b)
        s_3D = []
        for v in s:
            v_1 = np.reshape(v, (Views, samples))
            s_3D.append(v_1)
        print('s_3shape=', np.array(s_3D).shape)
#     binFile.close()
    return samples,Views,Views2,Slices,Echoes,Experiment,s_3D,etl

def Read_dat3(path):
    with open(path, 'rb') as binFile:
        b_samples = binFile.read(4)
        samples, = np.frombuffer(b_samples, dtype=np.int32)
        print('sampels=', samples)

        b_Views = binFile.read(4)
        Views = np.frombuffer(b_Views, dtype=np.int32)[0]
        print('Views=', Views)

        b_Slices = binFile.read(4)
        Slices = np.frombuffer(b_Slices, dtype=np.int32)[0]
        print('Slices=', Slices)

        b_imgtype = binFile.read(4)
        imgtype= np.frombuffer(b_imgtype, dtype=np.int32)[0]
        print('imgtype=',imgtype)

        b_pixel = binFile.read(4)
        pixel = np.frombuffer(b_pixel,dtype=np.int32)[0]
        print('pixel=',pixel)

        datasize = samples * Views * Slices * imgtype
        print(datasize)

    return samples, Views, Slices,datasize,imgtype,pixel
# In[ ]:
import re

def strsort(alist):
    def sort_key(s):
        # 鎺掑簭鍏抽敭瀛楀尮閰�
        # 鍖归厤寮€澶存暟瀛楀簭鍙�
        if s:
            try:
                c = re.findall('^\d+', s)[4]
            except:
                c = -1
            return int(c)
    alist.sort(key=sort_key)
    return alist

def order_fse(K,Samples,ETL):#K涓哄緟鎺掑簭鐨凢SE浜岀淮鐭╅樀
    m = np.array([K[i:i+ETL] for i in range(0,len(K),ETL)]) #鍒涘缓涓€涓笁缁寸煩闃靛苟鎸夌収ETL鏁板垝鍒嗕簩缁寸煩闃碉紝姣忎竴涓煩闃靛搴斾竴涓狟urst
    r = np.array([m[:,j,:] for j in range(ETL)]) #姣忎竴涓簩缁寸煩闃电殑鐩稿悓浣嶇疆琛屾爣鍓嶅悗缁勫悎涓虹洰鏍囨帓搴忎綅缃紝灏嗘帓搴忓ソ鐨勬瘡涓簩缁寸煩闃电粍鍚堟垚涓€涓柊涓夌淮鐭╅樀
    d = np.reshape(r,(-1,Samples))#鍦ㄦ帓搴忓ソ鐨勬柊涓夌淮鐭╅樀鎸夌収Samples鏁伴噸鏂板睍骞充负鎺掑簭瀹屾瘯鐨勪簩缁寸煩闃碉紝姝ゆ椂缂虹渷鐨�-1涓篤iews
    return d#杩斿洖鎺掑簭瀹屾垚鐨勪簩缁寸煩闃�

def preorder(k,order_list):   
#k涓哄緟鎺掑簭K绌洪棿鐭╅樀锛宱rder_list涓烘壂鎻忓簭鍙风煩闃碉紝杩斿洖鎸夌収鎵弿鐭╅樀搴忓彿鎺掑簭鍚庣殑K绌洪棿鐭╅樀
    zk = np.zeros_like(k)
    i=0
    for k1 in order_list:
        zk[int(k1)]= k[i]
        i+=1
    return zk
#瀵逛竴涓簩缁寸煩闃电殑姣忎竴琛屽仛鍌呴噷鍙跺彉鎹�
def fft1(img):
    row_fft = []
    for r in img:
        row_fft.append(np.fft.ifft(r))
    return row_fft
#杈撳叆鏈夋晥鐩镐綅缂栫爜姝ユ暟锛屾湁鏁圗TL锛屾湁鏁圗TL绐楀彛宸︺€佸彸鐨勬姏鍘籯绾挎暟锛岃繑鍥�0K鍦ㄥ乏鎶涘悗鐨勭涓€鏍筀绾夸笂
def write_scan(views,etl,dummy_num1,dummy_num2):
    list_1 = []
    dummy1 = [int(views/2)] * dummy_num1
    dummy2 = [int(views/2)] * dummy_num2
    for i in range(int(views/(etl*2))):
        l1 = np.arange(int(views/2) + i,int(views),int(views/(etl*2)))
        l1_d = np.hstack(((dummy1),l1))
        l1_d2 = np.hstack((l1_d,dummy2))
        list_1.append(l1_d2)
        l2 = np.arange(i,int(views/2),int(views/(etl*2)))[::-1]
        l2_d = np.hstack(((dummy1),l2))
        l2_d2 = np.hstack((l2_d,dummy2))
        list_1.append(l2_d2)
    list1 = np.array(list_1)
    list2 = np.reshape(list1,(-1,))
    if dummy_num1 == 0:
        list2 = [int(f) for f in list2]
    elif dummy_num2 == 0:
        list2 = [int(f) for f in list2]
    return list2
#0K鏀惧湪dummy鍚庣涓€鏍癸紝杩斿洖鎺掑簭搴忓彿
def write_ord(views,etl,dummy_num1,dummy_num2):
    list_1 = []
    dummy1 = [int(2000)] * dummy_num1
    dummy2 = [int(2000)] * dummy_num2
    for i in range(int(views/(etl*2))):
        l1 = np.arange(int(views/2) + i,int(views),int(views/(etl*2)))
        l1_d = np.hstack(((dummy1),l1))
        l1_d2 = np.hstack((l1_d,dummy2))
        list_1.append(l1_d2)
        l2 = np.arange(i,int(views/2),int(views/(etl*2)))[::-1]
        l2_d = np.hstack(((dummy1),l2))
        l2_d2 = np.hstack((l2_d,dummy2))
        list_1.append(l2_d2)
    list1 = np.array(list_1)
    list2 = np.reshape(list1,(-1,))
    list2 = np.insert(list2,0,len(list2))
    if dummy_num1 == 0:
        list2 = [int(f) for f in list2]
    elif dummy_num2 == 0:
        list2 = [int(f) for f in list2]
    return list2
#杈撳叆鏈仛姹夋槑绐楃殑涓夌淮K鐭╅樀锛岃緭鍑哄湪views2鏂瑰悜涓婂姞绐楀悗鐨勪笁缁寸煩闃�
#DV2 = Display Views2
def hamming(K,Samples,Views2,DV2):
    win_new = np.hamming(Views2)
    pad_win = np.pad(win_new, ((DV2-Views2)/2, (DV2-Views2)/2), 'constant')

    # 瀵逛竴涓簩缁寸煩闃电殑姣忎竴琛屽仛鍌呴噷鍙跺彉鎹�
    def fft1(img):
        row_fft = []
        for r in img:
            row_fft.append(np.fft.ifft(r))
        return row_fft

    pad_arr1 = []
    for p in K:
        img_p = np.fft.ifft2(p)
        #     shift_p = np.fft.fftshift(img_p)
        pad_arr1.append(img_p)
    swap_pad = np.array(pad_arr1).swapaxes(0, 2)  # 杞崲涓夌淮鐭╅樀杞�
    flat_swap = np.reshape(swap_pad, (-1, DV2))  # 浜岀淮灞曞钩
    z = []
    for e in flat_swap:
        conv2 = e * pad_win  # 鍔犲鐞嗗悗鐨勭獥
        #     conv3 = e*np.hamming(128)#鍔�128涓偣鐨勬眽鏄庣獥
        z.append(conv2)  # 灏嗗嵎绉悗鐨勬暟鎹祴鍊肩粰z
    # z_3d = np.reshape(z, (-1, Samples, DV2))
    # swap_z = np.array(z_3d).swapaxes(0, 2)

    z1 = fft1(z)  # 鍦╒iews2鏂瑰悜涓婂仛涓€缁村倕閲屽彾鍙嶅彉鎹�
    z_swap = np.reshape(z1, (-1, Samples, DV2))  # 鎭㈠涓轰笁缁寸煩闃�
    shift_conv = np.array(z_swap).swapaxes(0, 2)  # 鎭㈠杞�
    shift_c = np.fft.ifftshift(shift_conv)  # 绉婚
    return shift_c




