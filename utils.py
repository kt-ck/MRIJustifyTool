import re
import os
import numpy as np
from MRI_Utils import Read_XMD


def changeXPRFileWithParams(params, xpr_file):
    with open(xpr_file, 'r+') as f:
        content = f.read()
        data = []
        for param in params:
            regex = re.compile(
                param["key"] + r"\s*,\s*([-\d]+)", re.IGNORECASE)
            match_obj = re.search(regex, content)
            if not match_obj:
                print("XPR file does not include {} parameter".format(
                    param["key"]))
                return [{"status": False}]
            sentence_begin, sentence_end = match_obj.span()
            param["original_value_end"] = sentence_end
            original_value = match_obj.group(1)
            param["original_value"] = int(original_value)
            param["original_value_index"] = sentence_end - len(original_value)
            param["status"] = True
            data.append(param)
        data.sort(key=lambda x: x["original_value_index"])
        content_o = ""
        last_begin = 0
        for each in data:
            content_o += content[last_begin:each["original_value_index"]]
            if each["value"] == -1:
                content_o += str(each["original_value"])
            else:
                content_o += str(each["value"])
            last_begin = each["original_value_end"]
        content_o += content[last_begin:]

    with open(xpr_file, 'w+') as f:
        f.seek(0, 0)
        f.writelines(content_o)

    return data


def getXMD3DData(xmd_file_path):
    (offset, samples, Views, Views2, Slices, Echoes, Experiments,
     Nex, Chennels, datasize) = Read_XMD(xmd_file_path)
    with open(xmd_file_path, 'rb') as xmd_bfile:
        imgRawData = []
        xmd_bfile.seek(offset, 0)
        for i in range(datasize // 2):
            real_b = xmd_bfile.read(4)
            real_float = np.frombuffer(real_b, dtype=np.float32)[0]

            im_b = xmd_bfile.read(4)

            im_float = np.frombuffer(im_b, dtype=np.float32)[0]
            cplx = real_float + im_float * 1j
            imgRawData.append(cplx)
        s = []

        for i in range(0, len(imgRawData), samples * Views):
            temp = imgRawData[i: i + samples * Views]
            s.append(temp)
        s_3D = []

        for each in s:
            temp = np.reshape(each, (Views, samples))
            s_3D.append(temp)

        return s_3D


def getXMDFullData(xmd_file_path):
    (offset, samples, Views, Views2, Slices, Echoes, Experiments,
     Nex, Chennels, datasize) = Read_XMD(xmd_file_path)
    with open(xmd_file_path, 'rb') as xmd_bfile:
        imgRawData = []
        xmd_bfile.seek(offset, 0)
        for i in range(datasize // 2):
            real_b = xmd_bfile.read(4)
            real_float = np.frombuffer(real_b, dtype=np.float32)[0]

            im_b = xmd_bfile.read(4)

            im_float = np.frombuffer(im_b, dtype=np.float32)[0]
            cplx = real_float + im_float * 1j
            imgRawData.append(cplx)
        s = []

        for i in range(0, len(imgRawData), samples * Views):
            temp = imgRawData[i: i + samples * Views]
            s.append(temp)
        s_3D = []

        for each in s:
            temp = np.reshape(each, (Views, samples))
            s_3D.append(temp)

        return {
            "offset": offset,
            "samples": samples,
            "Views": Views,
            "Views2": Views2,
            "Slices": Slices,
            "Echoes": Echoes,
            "Experiments": Experiments,
            "Nex": Nex,
            "Chennels": Chennels,
            "datasize": datasize,
            "s_3D": s_3D
        }


def findBestChannel(xmd_dir):
    max_adc = -1
    target_file = ""
    for xmd_file in os.listdir(xmd_dir):
        s_3D = getXMD3DData(os.path.join(xmd_dir, xmd_file))

        adc = np.max(
            np.array([np.max(np.real(s_3D[0])), np.max(np.imag(s_3D[0]))]))
        print(adc)
        if adc > max_adc:
            target_file = xmd_file
            max_adc = adc

    s_3D = getXMD3DData(os.path.join(xmd_dir, target_file))
    channel = -1
    max_adc = -1
    for c in range(len(s_3D)):
        adc = np.max(
            np.array([np.max(np.real(s_3D[c])), np.max(np.imag(s_3D[c]))]))
        if max_adc < adc:
            max_adc = adc
            channel = c

    return target_file, max_adc, channel


if __name__ == "__main__":
    print(changeXPRFileWithParams([{"key": "G3", "value": 12}, {
          "key": "NO_VIEWS", "value": 0}, {"key": "G2", "value": 0}], "XGYMR.XPR"))
