
import numpy as np
import ctypes
from ctypes import c_int, create_string_buffer, byref
import re
import sys
import os
import time
import shutil
from utils import changeXPRFileWithParams, findBestChannel, getXMDFullData

##global paramters
#
Dll_path = r"D:\py2xms_210311\py2xms_210311\callerdll\\clientcaller.dll"
XGYMR_XPR = r'D:\MedView\XMS\XGYMR.XPR'
# XGYMR_XPR = 'XGYMR.XPR'
save_pt = r'D:\test_auto10'
optimal_xmd_file = ""
optimal_channel = -1


def sendXPRFile(param_list, temp_dir):
    global save_pt, mydll
    save_path = os.path.join(save_pt, temp_dir)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    data = changeXPRFileWithParams(param_list, XGYMR_XPR)

    if len(data) != 0 and data[0]["status"] == False:
        sys.exit()

    save_pstr = bytes(save_path, "utf8")

    mydll.xms_readSysParam()
    mydll.xms_setSavePath(save_pstr)

    pstr = bytes(XGYMR_XPR, "utf8")

    mydll.xms_sendParamFile(pstr)
    time.sleep(1)
    mydll.xms_startScan()

    prerow = c_int(-1)
    state = c_int(-2)
    currow = c_int(0)
    totalrow = c_int(0)

    szDataFilePath = create_string_buffer(100)

    a = 1
    while a < 100:
        mydll.xms_getState(byref(state))
        if state.value == 2:
            mydll.xms_getProgress(byref(currow), byref(totalrow))
            if currow.value != prerow.value:
                if currow.value == totalrow.value:
                    print("\r", "progress:", currow.value, "/",
                          totalrow.value, end="\n", flush=True)
                else:
                    print("\r", "progress:", currow.value, "/",
                          totalrow.value, end="", flush=True)
                prerow.value = currow.value
        elif state.value == 5:
            print('scan success')
            mydll.xms_getDataFilePath(byref(szDataFilePath), 100)
            print(szDataFilePath.value)
            break
        elif state.value == 6:
            print('scan stop')
            break
        elif state.value == 4:
            print('scan error')
            break
        time.sleep(1)
    if state.value == 4 or state.value == 6:
        return {'status': False}

    return {'status': True, "data": data}


def getInfoWithParams(param_list, temp_dir):
    # when G3 = -1, G3 equals the original G3 from XPR file
    # temp_dir saves temp xmd file
    global save_pt, mydll
    save_path = os.path.join(save_pt, temp_dir)
    rtn_data = sendXPRFile(param_list, temp_dir)
    if not rtn_data["status"]:
        return {"status": False}

    xmd_data = getXMDFullData(os.path.join(save_path, optimal_xmd_file))
    s_3D = xmd_data["s_3D"]
    samples = xmd_data["samples"]
    Views = xmd_data["Views"]

    abs_k = np.abs(s_3D[optimal_channel])
    # print(abs_k.shape)
    pos = np.unravel_index(np.argmax(abs_k[0]), abs_k[0].shape)[0] + 1
    # print(pos)
    nmax = int(np.max(abs_k[0]))
    return {"status": True,
            "params": {"pos": pos, "nmax": nmax, "samples": samples, "views": Views, "param_info": rtn_data["data"],
                       "abs_k": abs_k}}


def FSELocalConfig():
    global optimal_xmd_file

    with open(XGYMR_XPR, 'r+') as f:
        content = f.read()
        regex = re.compile(r"views_per_seg\s*,\s*(\d+)", re.IGNORECASE)
        match_obj = re.search(regex, content)
        views_per_seg = int(match_obj.group(1))

        regex = re.compile(r"NO_Views\s*,\s*(\d+)", re.IGNORECASE)
        match_obj = re.search(regex, content)
        begin, end = match_obj.span()
        length = len(match_obj.group(1))
        content_o = content[:end - length] + str(views_per_seg) + content[end:]

    with open(XGYMR_XPR, "w+") as f:
        f.seek(0, 0)
        f.writelines(content_o)

    changeXPRFileWithParams([{"key": "VIEWS2", "value": 1}], XGYMR_XPR)
    changeXPRFileWithParams([{"key": "gp_on", "value": 0}], XGYMR_XPR)


def init():
    global optimal_xmd_file, optimal_channel
    FSELocalConfig()
    sendXPRFile([], "-1")
    optimal_xmd_file, _, optimal_channel = findBestChannel(
        os.path.join(save_pt, "-1"))


def Justify_FSE(thread, messageThread, X1, Z2_enable=False, xpr_path=XGYMR_XPR, cache_dir=save_pt, dll_path=Dll_path,
                G3_scale=1, G3_step=2, symmetry_step=2, symmetry_scale=1, T6_scale1=1, T6_scale2=1, G3_distinct=0.2, t6_distinct=0.7, ratio=-1):
    global XGYMR_XPR, save_pt, Dll_path, mydll
    Dll_path = dll_path
    XGYMR_XPR = xpr_path
    save_pt = cache_dir
    # messageThread.show(100, "initialize data ...")
    thread.info = "Info: initialize data ..."
    thread.show()
    mydll = ctypes.cdll.LoadLibrary(Dll_path)
    mydll.xms_init()
    mydll.xms_launchApp()

    last_G3 = -1
    last_T6 = -1
    direction = 0
    positive = 1

    print("Justify_FSE is called")
    # delete xmd dir
    if os.path.exists(save_pt):
        shutil.rmtree(save_pt)

    init()
    print("optimal channel = {}".format(optimal_xmd_file))
    print("optimal c={}".format(optimal_channel))
    # messageThread.show(101, "code is running ...")
    thread.info = "Info: code is running ..."
    thread.show()
    if thread.X1_enable:
        for i in range(10000):
            if thread.stopped():
                thread.info = "Info: pause ..."
                thread.show()
                sys.exit()
            FSELocalConfig()
            dataObj = getInfoWithParams([{"key": "G3", "value": last_G3}, {
                                        "key": "T6", "value": last_T6}], str(i + 1))
            if dataObj["status"]:
                pos = dataObj["params"]["pos"]
                nmax = dataObj["params"]["nmax"]
                samples = dataObj["params"]["samples"]
                param_info = dataObj["params"]["param_info"]
                for param in param_info:
                    if "G3" == param["key"]:
                        original_G3 = param["original_value"] if i <= 1 else param["value"]
                    elif "T6" == param["key"]:
                        original_T6 = param["original_value"] if i <= 1 else param["value"]

                positive = -1 if original_G3 < 0 else 1
                original_G3 = abs(original_G3)

                last_G3 = abs(last_G3)

                abs_k = dataObj["params"]["abs_k"]

                target_pos = samples // 2 + 1

                left = int(np.mean(abs_k[0][target_pos - 10: target_pos]))
                right = int(
                    np.mean(abs_k[0][-samples // 2:-samples // 2 + 10]))

                _pos = np.argmax(abs_k, axis=1)
                print("_pos = {}".format(_pos + 1))

                t6_left = int(
                    np.mean(np.mean(abs_k[:, samples//2 - 10:samples // 2], axis=1)))
                t6_right = int(
                    np.mean(np.mean(abs_k[:, -samples // 2:-samples // 2 + 10], axis=1)))
                k = np.array([i for i in range(len(_pos), 0, -1)])
                pos_distinct = np.sum((_pos + 1 - target_pos)*k)
                error_break = 20
                infinite = 100000000
                if direction != 0:
                    if pos != target_pos or abs((right - left)) / left >= G3_distinct:
                        if (pos - target_pos > 0 and direction == -1) or (pos - target_pos < 0 and direction == 1):
                            G3_scale += 1
                            if G3_scale >= error_break:
                                thread.info = "Info: Maybe G3 step is really large, so restart algorithm ..."
                                thread.show()
                                time.sleep(1)
                                return Justify_FSE(thread, messageThread, int(positive*original_G3 * ratio), Z2_enable, xpr_path, cache_dir, dll_path, 1, 2, 3, 3, T6_scale1, T6_scale2)
                        elif pos != target_pos:
                            G3_scale = G3_scale // 2 if G3_scale >= 3 else 1
                        elif pos == target_pos:
                            if (right - left > 0 and direction == -1) or (right-left < 0 and direction == 1):
                                symmetry_scale += 1
                            else:
                                symmetry_scale = symmetry_scale // 2 if symmetry_scale >= 3 else 1
                        last_G3 = original_G3 - np.sign(pos - target_pos) * G3_step * G3_scale ** 2 - symmetry_step * int(
                            np.sign(right - left) / (1 + infinite*abs(pos - target_pos))) * symmetry_scale
                        last_T6 = original_T6
                    else:
                        if pos_distinct == 0:
                            if (t6_right - t6_left > 0 and direction < 0) or (t6_right - t6_left < 0 and direction > 0):
                                T6_scale2 += 1
                            elif (t6_right - t6_left > 0 and direction > 0) or (t6_right-t6_left < 0 and direction < 0):
                                T6_scale2 = T6_scale2 // 2 if T6_scale2 >= 3 else 1
                        else:
                            if (pos_distinct < 0 and direction > 0) or (pos_distinct > 0 and direction < 0):
                                T6_scale1 += 1
                            elif (pos_distinct > 0 and direction > 0) or (pos_distinct < 0 and direction < 0):
                                T6_scale1 = T6_scale1 // 2 if T6_scale1 >= 3 else 1
                        last_G3 = original_G3
                        last_T6 = original_T6 - T6_scale1 * np.sign(pos_distinct) * 6 - int(
                            T6_scale2 * np.sign((t6_right - t6_left)/(1+abs(pos_distinct)*infinite))) * 6

                else:
                    last_G3 = original_G3
                    last_T6 = original_T6
                    if ratio == -1:
                        ratio = X1 / (original_G3 * positive)

                direction = -1 if pos - target_pos > 0 or (pos == target_pos and abs((right - left)) / left >= G3_distinct and right-left > 0) \
                    or (pos == target_pos and abs((right - left)) / left < G3_distinct and (pos_distinct > 0 or last_T6 - original_T6 < 0)) else 1

                last_G3 = positive * last_G3
                print(abs((right - left)) / left)
                print(
                    "G3 = {}, new_G3 = {},target_pos = {}, pos = {}, left = {}, right = {}, G3_scale = {}, symmetry_scale={}".format(
                        original_G3, last_G3, target_pos, pos, left, right, G3_scale, symmetry_scale))
                print("T6 = {}, new_T6 = {},pos_distinct={},t6_left={},t6_right={}, T6_scale1 = {},T6_scale2={} direction={}".format(
                    original_T6, last_T6, pos_distinct, t6_left, t6_right, T6_scale1, T6_scale2, direction))
                print(abs(t6_right - t6_left) / t6_left)

                _pos_list = _pos.tolist()
                print(len(_pos_list))
                if len(_pos_list) > 10:
                    thread.info = "Info: pos = ["

                    for index in range(10):
                        if index != 0:
                            thread.info += ","
                        thread.info += str(_pos_list[index])
                    thread.info += "...]"
                else:
                    thread.info = "Info: pos = {}".format(_pos)
                    thread.show()
                thread.data = {"G3": positive * original_G3,
                               "T6": original_T6,
                               "abs_k": abs_k,
                               "optimal_layer": optimal_channel,
                               "optimal_channel": optimal_xmd_file,
                               "G3_ratio": ratio,
                               "t6_reference": abs(t6_right - t6_left) / t6_left,
                               "G3_reference": abs((right - left)) / left
                               }
                thread.show()

                if pos == target_pos and abs((right - left)) / left < G3_distinct and pos_distinct == 0 and abs(t6_right - t6_left) / t6_left < t6_distinct:
                    break

            else:
                print("some error occurs")
                messageThread.show(
                    500, "can not send the XPR file, please check the XPR file.")
                thread.stop()
                sys.exit()
        optimal_G3 = positive*original_G3
        X1 = int(positive*original_G3 * ratio)
    if Z2_enable:
        thread.info = "Info: Justify G2 paramter ..."
        thread.show()
        dataObj = getInfoWithParams([{"key": "G3", "value": -1}, {
            "key": "T6", "value": -1}, {
            "key": "G2", "value": -1
        }], "Z2_0")
        param_info = dataObj["params"]["param_info"]
        for param in param_info:
            if "G2" == param["key"]:
                last_G2 = param["original_value"]
            if "G3" == param["key"]:
                optimal_G3 = param["original_value"]
            elif "T6" == param["key"]:
                original_T6 = param["original_value"]

        thread.original_G2 = last_G2
        last_abs_k = dataObj["params"]["abs_k"]
        last_max_k = np.max(last_abs_k, axis=1)
        direction = 1
        new_G2 = last_G2 + 3
        G2_scale = 1
        G2_step = 3
        count = 0
        for i in range(10000):
            if thread.stopped():
                thread.info = "Info: pause ..."
                thread.show()
                sys.exit()
            dataObj = getInfoWithParams([{
                "key": "G2", "value": new_G2
            }], "Z2_{}".format(i+1))

            param_info = dataObj["params"]["param_info"]
            new_abs_k = dataObj["params"]["abs_k"]
            new_max_k = np.max(new_abs_k, axis=1)

            delta_k = np.sum(new_max_k) - np.sum(last_max_k)
            if delta_k > 0:
                G2_scale += 1
            else:
                G2_scale = G2_scale // 2 if G2_scale >= 3 else 1
                count += 1

            last_G2 = new_G2
            new_G2 = new_G2 + int(direction * G2_step *
                                  G2_scale * np.sign(delta_k))

            abs_k = new_abs_k
            direction = np.sign(new_G2 - last_G2)
            print("new_G2={}, last_G2={}, new_abs={}, last_abs={},delta_k={}, count={}".format(
                new_G2, last_G2, np.sum(new_max_k), np.sum(last_max_k), delta_k, count))
            if count > 10:
                break
            thread.data = {"G3": optimal_G3,
                           "T6": original_T6,
                           "abs_k": new_abs_k,
                           "G2": new_G2,
                           "G2_enable": True,
                           "optimal_layer": optimal_channel,
                           "optimal_channel": optimal_xmd_file,
                           }
            if thread.X1_enable:
                thread.data["G3_ratio"] = ratio
            thread.show()
        optimal_G2 = new_G2 if delta_k > 0 else last_G2
        thread.G2 = optimal_G2
    thread.info = "Info: Done ..."
    thread.show()
    thread.stop()

    return optimal_G3, abs_k, original_T6, optimal_channel, optimal_xmd_file, X1


if __name__ == "__main__":
    print(Justify_FSE())
