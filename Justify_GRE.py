import numpy as np
import ctypes
from ctypes import c_int, create_string_buffer, byref
import sys
import os
import time
import shutil
from utils import changeXPRFileWithParams, findBestChannel, getXMDFullData


##global paramters
#
Dll_path = r"D:\py2xms_210311\py2xms_210311\callerdll\\clientcaller.dll"

XGYMR_XPR = r'C:\Users\XGY\Desktop\XGYMR.XPR'
# XGYMR_XPR = 'XGYMR.XPR'
save_pt = r'D:\test_auto'

optimal_xmd_file = ""
optimal_layer = -1


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

    abs_k = np.abs(s_3D[optimal_layer])
    # print(abs_k.shape)
    pos = np.unravel_index(np.argmax(abs_k[0]), abs_k[0].shape)[0] + 1
    # print(pos)
    nmax = int(np.max(abs_k[0]))
    return {"status": True,
            "params": {"pos": pos, "nmax": nmax, "samples": samples, "views": Views, "param_info": rtn_data["data"],
                       "abs_k": abs_k}}


def GRELocalConfig():
    changeXPRFileWithParams([{"key": "NO_VIEWS", "value": 1}, {
                            "key": "gp_on", "value": 0}], XGYMR_XPR)


def init():
    global optimal_xmd_file, optimal_layer
    GRELocalConfig()
    sendXPRFile([], "-1")
    optimal_xmd_file, _, optimal_layer = findBestChannel(
        os.path.join(save_pt, "-1"))


def findOptimalG3(thread, X1, G2_enable=False, xpr_path=XGYMR_XPR, cache_dir=save_pt, dll_path=Dll_path, G3_distinct=0.3, G3_scale=1, G3_step=2, symmetry_step=2, symmetry_scale=1, ratio=-1):
    global XGYMR_XPR, save_pt, Dll_path, mydll
    XGYMR_XPR = xpr_path
    save_pt = cache_dir
    Dll_path = dll_path
    mydll = ctypes.cdll.LoadLibrary(Dll_path)
    thread.info = "Info: initialize data ..."
    thread.show()
    mydll.xms_init()
    mydll.xms_launchApp()

    init()
    direction = 0
    last_G3 = -1
    # delete xmd dir
    shutil.rmtree(save_pt)
    infinite = 1000000
    error_break = 20
    positive = 1
    new_X1 = -1

    thread.info = "Info: code is running ..."
    thread.show()

    if thread.X1_enable:
        for i in range(10000):
            if thread.stopped():
                thread.info = "Info: pause ..."
                thread.show()
                sys.exit()
            dataObj = getInfoWithParams(
                [{"key": "G3", "value": last_G3}], str(i + 1))
            if dataObj["status"]:
                pos = dataObj["params"]["pos"]
                nmax = dataObj["params"]["nmax"]
                samples = dataObj["params"]["samples"]
                param_info = dataObj["params"]["param_info"]
                for param in param_info:
                    if "G3" == param["key"]:
                        original_G3 = param["original_value"] if i <= 1 else param["value"]
                positive = -1 if original_G3 < 0 else 1
                original_G3 = abs(original_G3)
                # angle = dataObj["params"]["angle"]
                abs_k = dataObj["params"]["abs_k"]
                target_pos = samples // 2 + 1
                left = int(np.mean(abs_k[0][target_pos - 10:target_pos]))
                right = int(
                    np.mean(abs_k[0][-samples // 2:-samples // 2 + 10]))
                if direction != 0:
                    if pos != target_pos or abs((right - left)) / left >= G3_distinct:
                        if (pos - target_pos > 0 and direction == -1) or (pos - target_pos < 0 and direction == 1):
                            G3_scale += 1
                            if G3_scale >= error_break:
                                thread.info = "Info: Maybe G3 step is really large, so restart algorithm ..."
                                thread.show()
                                time.sleep(1)
                                return findOptimalG3(thread, int(positive*original_G3 * ratio), G2_enable, ratio=ratio, xpr_path=XGYMR_XPR, cache_dir=save_pt, dll_path=Dll_path, G3_distinct=G3_distinct, G3_scale=1, G3_step=2, symmetry_step=2, symmetry_scale=0.6)
                        elif pos != target_pos:
                            # return findOptimalG3(thread, int(positive*original_G3 * ratio), ratio=ratio, xpr_path=XGYMR_XPR, cache_dir=save_pt, dll_path=Dll_path, G3_distinct=G3_distinct, G3_scale=1, G3_step=2, symmetry_step=2, symmetry_scale=0.6)
                            G3_scale = G3_scale // 2 if G3_scale >= 3 else 1
                        elif pos == target_pos:
                            if (right - left > 0 and direction == -1) or (right-left < 0 and direction == 1):
                                symmetry_scale += 1
                            else:
                                symmetry_scale = symmetry_scale // 2 if symmetry_scale >= 3 else 1
                        last_G3 = original_G3 - np.sign(pos - target_pos) * G3_step * G3_scale ** 2 - symmetry_step * int(
                            np.sign(right - left) / (1 + infinite*abs(pos - target_pos)) * symmetry_scale)

                else:
                    last_G3 = original_G3
                    if ratio == -1:
                        ratio = X1 / (original_G3 * positive)

                print("last_G3={},G3={},pos={},target_pos={},G3_scale={},s_scale={}".format(
                    last_G3, original_G3, pos, target_pos, G3_scale, symmetry_scale))
                direction = -1 if pos - target_pos > 0 or (pos == target_pos and abs((right - left)) / left >= G3_distinct and right-left > 0) \
                    or (pos == target_pos and abs((right - left)) / left < G3_distinct) else 1

                last_G3 = positive * last_G3

                thread.info = "Info: pos = {}".format(pos)
                thread.show()

                thread.data = {"G3": positive * original_G3,
                               "abs_k": abs_k,
                               "nmax": nmax,
                               "X1": int(positive*original_G3 * ratio),
                               "reference": abs((right - left)) / left,
                               "optimal_layer": optimal_layer,
                               "optimal_channel": optimal_xmd_file
                               }

                thread.show()
                if pos == target_pos and abs((right - left)) / left < G3_distinct:
                    break

            else:
                thread.info = "Error: can not send the XPR file, please check the XPR file."
                thread.show()
                sys.exit()

        optimal_G3 = positive * original_G3
        new_X1 = int(optimal_G3 * ratio)

    if G2_enable:
        thread.info = "Info: Justify G2 paramter ..."
        thread.show()
        dataObj = getInfoWithParams([{"key": "G3", "value": -1}, {
            "key": "G2", "value": -1
        }], "Z2_0")
        param_info = dataObj["params"]["param_info"]
        for param in param_info:
            if "G2" == param["key"]:
                last_G2 = param["original_value"]
            if "G3" == param["key"]:
                optimal_G3 = param["original_value"]
        thread.original_G2 = last_G2
        last_abs_k = dataObj["params"]["abs_k"]
        last_max_k = np.max(last_abs_k, axis=1)
        direction = 1
        new_G2 = last_G2 + 10
        G2_scale = 1
        G2_step = 6
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
            nmax = int(np.sum(new_max_k))
            direction = np.sign(new_G2 - last_G2)
            print("new_G2={}, last_G2={}, new_abs={}, last_abs={},delta_k={}, count={}".format(
                new_G2, last_G2, np.sum(new_max_k), np.sum(last_max_k), delta_k, count))
            if count > 10:
                break
            thread.data = {"G3": optimal_G3,
                           "abs_k": new_abs_k,
                           "G2": new_G2,
                           "G2_enable": True,
                           "nmax": nmax,
                           "optimal_layer": optimal_layer,
                           "optimal_channel": optimal_xmd_file
                           }

            if thread.X1_enable:
                thread.data["X1"] = int(optimal_G3 * ratio)
            thread.show()
        optimal_G2 = new_G2 if delta_k > 0 else last_G2
        thread.G2 = optimal_G2
        abs_k = new_abs_k
    thread.info = "Info: Done ..."
    thread.show()
    thread.stop()
    return optimal_G3, nmax, abs_k, new_X1


if __name__ == "__main__":
    findOptimalG3()
