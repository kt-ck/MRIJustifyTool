# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
# http://www.wxformbuilder.org/
##
# PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.lib.plot as plot
from Justify_GRE import findOptimalG3
from Justify_FSE import Justify_FSE
import threading
import time
##########################################################################
# Class Thread
#########################################################################


class GREThread (threading.Thread):
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame
        self._stop = threading.Event()
        self.data = {}
        self._show = threading.Event()
        self.info = ""

    def show(self):
        self._show.set()

    def isShow(self):
        return self._show.isSet()

    def run(self):
        self.frame.runGREJustify(self)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class GREDraw(threading.Thread):
    def __init__(self, frame, GREThread):
        threading.Thread.__init__(self)
        self.frame = frame
        self.GREThread = GREThread

    def run(self):
        while not self.GREThread.stopped():
            if self.GREThread._show.wait():
                self.frame.drawGREData()
                self.GREThread._show.clear()
                print("draw done")


class FSEThread (threading.Thread):
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame
        self._stop = threading.Event()
        self.data = {}
        self._show = threading.Event()
        self.info = ""
        self._infoshow = threading.Event()
        self.G2_enable = False
        self.G2 = 0
        self.original_Z2 = 0
        self.original_G2 = 0

    def run(self):
        self.frame.runFSEJustify(self)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def show(self):
        self._show.set()

    def isShow(self):
        return self._show.isSet()

    def infoShow(self):
        self._infoshow.set()

    def isInfoShow(self):
        return self._infoshow.isSet()


class FSEABSKDraw (threading.Thread):
    def __init__(self, frame, FSEThread):
        threading.Thread.__init__(self)
        self.frame = frame
        self.FSEThread = FSEThread

    def run(self):
        while not self.FSEThread.stopped():
            if self.FSEThread._show.wait():
                self.frame.drawFSEData()
                self.FSEThread._show.clear()
                print("draw done")


class MessageManager(threading.Thread):
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame
        self.queue = []
        self._show = threading.Event()
        self._stop = threading.Event()

    def show(self, code, message):
        self.queue.append({"code": code, "message": message})
        self._show.set()

    def isShow(self):
        return self._show.isSet()

    def stop(self):
        self._stop.set()

    def isStop(self):
        return self._stop.isSet()

    def run(self):
        while not self.isStop():
            if self._show.wait():
                print("message manager is set")
                notification = self.queue.pop(0)
                m = wx.MessageDialog(self.frame, notification["message"], "info: "+str(
                    notification["code"]), wx.YES_DEFAULT | wx.ICON_QUESTION)
                if m.ShowModal() == wx.ID_YES:
                    m.Destroy()
                self._show.clear()
        print("message manager exit")

###########################################################################
# Class MyFrame1
###########################################################################


class MyFrame1 (wx.Frame):

    def __init__(self, parent):
        self.FSE_Z2_enable = False
        self.GRE_Z2_enable = False
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Params Dev Tool", pos=wx.DefaultPosition, size=wx.Size(
            1080, 700), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        wSizer1 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText2 = wx.StaticText(
            self, wx.ID_ANY, u"XGYMR_XPR FILE", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText2.Wrap(-1)

        wSizer1.Add(self.m_staticText2, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_filePicker1 = wx.FilePickerCtrl(
            self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)
        wSizer1.Add(self.m_filePicker1, 0, wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(
            self, wx.ID_ANY, u"CACHE DIR", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)

        wSizer1.Add(self.m_staticText4, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_dirPicker2 = wx.DirPickerCtrl(
            self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        wSizer1.Add(self.m_dirPicker2, 0, wx.ALL, 5)

        self.m_staticText6 = wx.StaticText(
            self, wx.ID_ANY, u"DLL FILE", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)

        wSizer1.Add(self.m_staticText6, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_filePicker3 = wx.FilePickerCtrl(
            self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.Size(-1, -1), wx.FLP_DEFAULT_STYLE)
        wSizer1.Add(self.m_filePicker3, 0, wx.ALL, 5)

        bSizer4.Add(wSizer1, 1, wx.EXPAND, 5)

        self.m_staticline2 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer4.Add(self.m_staticline2, 0, wx.EXPAND | wx.ALL, 5)

        bSizer6 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(
            self, wx.ID_ANY, u"GRE Dev Tool", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText1.Wrap(-1)

        bSizer6.Add(self.m_staticText1, 0, wx.ALL, 5)

        bSizer10 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer7 = wx.BoxSizer(wx.VERTICAL)

        bSizer30 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText20 = wx.StaticText(
            self, wx.ID_ANY, u"X1", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText20.Wrap(-1)

        self.m_textCtrl20 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer30.Add(self.m_staticText20, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer30.Add(self.m_textCtrl20, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)

        self.cb1 = wx.CheckBox(
            self, wx.ID_ANY, 'G2 Enable', wx.DefaultPosition)
        self.m_textCtrl21 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer30.Add(self.cb1, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer30.Add(self.m_textCtrl21, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_CHECKBOX, self.onGREG2Enable)

        bSizer7.Add(bSizer30, 1, wx.LEFT, 5)

        bSizer12 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText7 = wx.StaticText(
            self, wx.ID_ANY, u"Reference:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText7.Wrap(-1)

        bSizer12.Add(self.m_staticText7, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_staticText16 = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer12.Add(self.m_staticText16, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer7.Add(bSizer12, 1, wx.LEFT, 5)

        bSizer13 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText8 = wx.StaticText(
            self, wx.ID_ANY, u"Degree Of Symmetry", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText8.Wrap(-1)

        bSizer13.Add(self.m_staticText8, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrl5 = wx.TextCtrl(
            self, wx.ID_ANY, u"0.5", wx.Point(-1, -1), wx.DefaultSize, 0)
        bSizer13.Add(self.m_textCtrl5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer7.Add(bSizer13, 1, wx.LEFT, 5)

        bSizer20 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_button1 = wx.Button(
            self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button4 = wx.Button(
            self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer20.Add(self.m_button1, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer20.Add(self.m_button4, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer7.Add(bSizer20, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL |
                    wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_button1.Bind(wx.EVT_BUTTON, self.GRESectionRunBtnOnClick)
        self.m_button4.Bind(wx.EVT_BUTTON, self.GRESectionStopBtnOnClick)

        bSizer10.Add(bSizer7, 1, wx.CENTER, 5)

        bSizer11 = wx.BoxSizer(wx.VERTICAL)

        bSizer21 = wx.BoxSizer(wx.VERTICAL)
        self.m_staticText15 = wx.StaticText(
            self, wx.ID_ANY, u"Info: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText40 = wx.StaticText(
            self, wx.ID_ANY, u"optimal_channel:          optimal_layer: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.plotter = plot.PlotCanvas(self)
        self.plotter.SetInitialSize(size=(700, 200))
        bSizer21.Add(self.m_staticText15, 0, wx.ALL, 5)
        bSizer21.Add(self.m_staticText40, 0, wx.ALL, 5)
        bSizer21.Add(self.plotter, 0, wx.ALL, 5)

        bSizer11.Add(bSizer21, 0, wx.ALL, 5)

        bSizer10.Add(bSizer11, 1, wx.EXPAND, 5)

        bSizer6.Add(bSizer10, 1, wx.EXPAND, 5)

        bSizer14 = wx.BoxSizer(wx.VERTICAL)
        self.m_staticText9 = wx.StaticText(
            self, wx.ID_ANY, u"FSE Dev Tool", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText9.Wrap(-1)

        bSizer14.Add(self.m_staticText9, 0, wx.ALL, 5)

        bSizer15 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer16 = wx.BoxSizer(wx.VERTICAL)

        bSizer21 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText10 = wx.StaticText(
            self, wx.ID_ANY, u"X1", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText10.Wrap(-1)
        bSizer21.Add(self.m_staticText10, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrl8 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer21.Add(self.m_textCtrl8, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.cb2 = wx.CheckBox(
            self, wx.ID_ANY, 'G2 Enable', wx.DefaultPosition)
        self.m_textCtrl22 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer21.Add(self.cb2, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer21.Add(self.m_textCtrl22, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_CHECKBOX, self.onFSEG2Enable)
        bSizer16.Add(bSizer21, 1, wx.LEFT, 5)

        bSizer17 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText10 = wx.StaticText(
            self, wx.ID_ANY, u"Degree Of The First Wave's Symmetry", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText10.Wrap(-1)
        bSizer17.Add(self.m_staticText10, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrl6 = wx.TextCtrl(
            self, wx.ID_ANY, u"0.2", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer17.Add(self.m_textCtrl6, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer22 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText12 = wx.StaticText(
            self, wx.ID_ANY, u"Reference:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText12.Wrap(-1)
        bSizer22.Add(self.m_staticText12, 1, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer16.Add(bSizer22, 1, wx.LEFT, 5)
        bSizer16.Add(bSizer17, 1, wx.LEFT, 5)

        bSizer18 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText11 = wx.StaticText(
            self, wx.ID_ANY, u"Degree Of All Waves' Sysmetry", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText11.Wrap(-1)
        bSizer18.Add(self.m_staticText11, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrl7 = wx.TextCtrl(
            self, wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer18.Add(self.m_textCtrl7, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer23 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText13 = wx.StaticText(
            self, wx.ID_ANY, u"Reference:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText13.Wrap(-1)
        bSizer23.Add(self.m_staticText13, 1, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer16.Add(bSizer23, 1, wx.LEFT, 5)
        bSizer16.Add(bSizer18, 1, wx.LEFT, 5)

        bSizer19 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_button2 = wx.Button(
            self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button3 = wx.Button(
            self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer19.Add(self.m_button2, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer19.Add(self.m_button3, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer16.Add(bSizer19, 1, wx.CENTER, 5)
        self.m_button2.Bind(wx.EVT_BUTTON, self.FSESectionRunBtnOnClick)
        self.m_button3.Bind(wx.EVT_BUTTON, self.FSESectionStopBtnOnClick)

        bSizer15.Add(bSizer16, 1, wx.CENTER, 5)

        bSizer22 = wx.BoxSizer(wx.VERTICAL)
        self.plotter1 = plot.PlotCanvas(self)
        self.plotter1.SetInitialSize(size=(700, 200))

        self.m_staticText14 = wx.StaticText(
            self, wx.ID_ANY, u"Info: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText41 = wx.StaticText(
            self, wx.ID_ANY, u"optimal_channel:          optimal_layer: ", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer22.Add(self.m_staticText14, 0, wx.ALL, 5)
        bSizer22.Add(self.m_staticText41, 0, wx.ALL, 5)
        bSizer22.Add(self.plotter1, 0, wx.ALL, 5)

        bSizer15.Add(bSizer22, 0, wx.ALL, 5)

        bSizer14.Add(bSizer15, 1, wx.CENTER, 5)

        bSizer4.Add(bSizer6, 1, wx.EXPAND, 5)

        self.m_staticline3 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer4.Add(self.m_staticline3, 0, wx.EXPAND | wx.ALL, 5)
        bSizer4.Add(bSizer14, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer4)
        self.Layout()

        self.Centre(wx.BOTH)
        self.Show()

        self.messageThread = MessageManager(frame=self)
        self.messageThread.start()

    def __del__(self):
        self.messageThread.stop()

    def getNeccessaryFilePath(self):
        self.XGYMR_XPR = self.m_filePicker1.GetPath()
        self.CACHE_DIR = self.m_dirPicker2.GetPath()
        self.DLL = self.m_filePicker3.GetPath()

        if not self.XGYMR_XPR:
            self.XGYMR_XPR = r'D:\MedView\XMS\XGYMR.XPR'

        if not self.CACHE_DIR:
            self.CACHE_DIR = r'D:\test_auto10'

        if not self.DLL:
            self.DLL = r"D:\py2xms_210311\py2xms_210311\callerdll\\clientcaller.dll"

    def FSESectionRunBtnOnClick(self, event):
        self.getNeccessaryFilePath()
        self.FSEChildThread = FSEThread(frame=self)
        self.FSEChildThread.start()

        self.drawFSEDataThread = FSEABSKDraw(
            frame=self, FSEThread=self.FSEChildThread)
        self.drawFSEDataThread.start()

    def FSESectionStopBtnOnClick(self, event):
        self.FSEChildThread.stop()

    def GRESectionStopBtnOnClick(self, event):
        self.GREChildThread.stop()

    def GRESectionRunBtnOnClick(self, event):
        self.getNeccessaryFilePath()
        self.GREChildThread = GREThread(frame=self)
        self.GREChildThread.start()
        self.drawGREDataThread = GREDraw(
            frame=self, GREThread=self.GREChildThread)
        self.drawGREDataThread.start()

    def onFSEG2Enable(self, event):
        cb = event.GetEventObject()
        if bool(cb.GetValue()):
            self.FSE_Z2_enable = True
        else:
            self.FSE_Z2_enable = False

    def onGREG2Enable(self, event):
        cb = event.GetEventObject()
        if bool(cb.GetValue()):
            self.GRE_Z2_enable = True
        else:
            self.GRE_Z2_enable = False

    def drawGREData(self):
        if "abs_k" in self.GREChildThread.data:
            G3 = self.GREChildThread.data["G3"]
            optimal_layer = self.GREChildThread.data["optimal_layer"]
            optimal_channel = self.GREChildThread.data["optimal_channel"]
            abs_k_list = self.GREChildThread.data["abs_k"][0]
            nmax = self.GREChildThread.data["nmax"]
            reference = str(self.GREChildThread.data["reference"])
            X1 = self.GREChildThread.data["X1"]
            self.m_staticText16.SetLabelText(reference)
            data = [[index, abs_k_list[index]]
                    for index in range(len(abs_k_list))]
            line = plot.PolyLine(data, colour='red', width=2)
            line2 = plot.PolyLine(
                [[len(abs_k_list) // 2, 0], [len(abs_k_list) // 2, nmax]], colour='blue', width=1)
            gc = plot.PlotGraphics([line, line2], 'G3={},nmax={},X1={}'.format(
                G3, nmax, X1))
            self.plotter.Draw(gc)
            self.m_staticText40.SetLabelText(
                "optimal_channel: {}        optimal_layer: {}".format(optimal_channel, optimal_layer))

        self.m_staticText15.SetLabelText(self.GREChildThread.info)

    def drawFSEData(self):
        if "abs_k" in self.FSEChildThread.data:
            if not "G2_enable" in self.FSEChildThread.data:
                optimal_layer = self.FSEChildThread.data["optimal_layer"]
                optimal_channel = self.FSEChildThread.data["optimal_channel"]
                g3_ref = self.FSEChildThread.data["G3_reference"]
                t6_ref = self.FSEChildThread.data["t6_reference"]
                self.m_staticText12.SetLabelText("Reference: " + str(g3_ref))
                self.m_staticText13.SetLabelText("Reference: " + str(t6_ref))
                self.m_staticText41.SetLabelText(
                    "optimal_channel: {}        optimal_layer: {}".format(optimal_channel, optimal_layer))
            else:
                G2 = self.FSEChildThread.data["G2"]
            abs_k_list = self.FSEChildThread.data["abs_k"]
            G3 = self.FSEChildThread.data["G3"]
            G3_ratio = self.FSEChildThread.data["G3_ratio"]
            T6 = self.FSEChildThread.data["T6"]
            data = []
            line_list = []
            for row_index in range(len(abs_k_list)):
                for col_index in range(len(abs_k_list[row_index])):
                    data.append(
                        [col_index + row_index * len(abs_k_list[row_index]), abs_k_list[row_index][col_index]])
                center = row_index * \
                    len(abs_k_list[row_index]) + \
                    len(abs_k_list[row_index]) // 2
                line_list.append(plot.PolyLine([[center, 0], [center, abs_k_list[row_index][len(
                    abs_k_list[row_index]) // 2 - 1]]], colour='blue', width=1))
            line = plot.PolyLine(data, colour='red', width=2)
            Z2 = int(G2 * (self.FSEChildThread.original_Z2 /
                     self.FSEChildThread.original_G2))
            if not self.FSE_Z2_enable:
                gc = plot.PlotGraphics([line] + line_list, 'G3={},T6={},X1={}'.format(
                    G3, T6, int(G3*G3_ratio)))
            else:
                gc = plot.PlotGraphics([line] + line_list, 'G3={},T6={},X1={},Z2={}'.format(
                    G3, T6, int(G3*G3_ratio), Z2))
            self.plotter1.Draw(gc)

        self.m_staticText14.SetLabelText(self.FSEChildThread.info)

    def runFSEJustify(self, thread):
        G3_distinct = self.m_textCtrl6.GetValue()
        T6_distinct = self.m_textCtrl7.GetValue()
        X1 = self.m_textCtrl8.GetValue()

        if X1 == "":
            self.messageThread.show(400, "X1 parameter not be typed.")
            return
        else:
            X1 = int(X1)
        if self.FSE_Z2_enable:
            thread.G2_enable = True
            original_Z2 = self.m_textCtrl22.GetValue()
            if original_Z2 != "":
                thread.original_Z2 = int(original_Z2)
            else:
                self.messageThread.show(400, "Z2 parameter not be typed.")
                return
        optimal_G3, nmax, abs_k, optiaml_T6, optimal_layer, optimal_channel, new_X1 = Justify_FSE(
            thread, self.messageThread, X1, self.FSE_Z2_enable, self.XGYMR_XPR, self.CACHE_DIR, self.DLL, G3_distinct=float(G3_distinct), t6_distinct=float(T6_distinct))

        abs_k_list = abs_k.tolist()
        data = []

        for row_index in range(len(abs_k_list)):
            for col_index in range(len(abs_k_list[row_index])):
                data.append(
                    [col_index + row_index * len(abs_k_list[row_index]), abs_k_list[row_index][col_index]])
        line = plot.PolyLine(data, colour='red', width=2)
        if self.FSE_Z2_enable:
            gc = plot.PlotGraphics([line], 'optimal_G3={},optimal_T6={},X1={},Z2={}'.format(
                optimal_G3, optiaml_T6, new_X1, int(thread.original_Z2 / thread.original_G2 * thread.G2)))
        else:
            gc = plot.PlotGraphics([line], 'optimal_G3={},optimal_T6={},X1={}'.format(
                optimal_G3, optiaml_T6, new_X1))
        self.plotter1.Draw(gc)

    def runGREJustify(self, thread):
        G3_distinct = float(self.m_textCtrl5.GetValue())
        X1 = self.m_textCtrl20.GetValue()
        if X1 == "":
            self.messageThread.show(400, "X1 parameter not be typed.")
            return
        else:
            X1 = int(X1)
        if self.XGYMR_XPR != "" or self.CACHE_DIR != "" or self.DLL != "":
            optimal_G3, nmax, abs_k, new_X1 = findOptimalG3(
                thread, X1, self.XGYMR_XPR, self.CACHE_DIR, self.DLL, G3_distinct=G3_distinct)
        else:
            optimal_G3, nmax, abs_k, new_X1 = findOptimalG3(
                thread, X1, G3_distinct=G3_distinct)
        time.sleep(1)
        abs_k_list = abs_k[0].tolist()
        data = [[x, abs_k_list[x]] for x in range(len(abs_k_list))]
        line = plot.PolyLine(data, colour='red', width=1)
        line2 = plot.PolyLine(
            [[len(abs_k_list) // 2, 0], [len(abs_k_list) // 2, nmax]], colour='blue', width=2)
        gc = plot.PlotGraphics(
            [line, line2], 'X1={},optimal_G3={},nmax={}'.format(new_X1, optimal_G3, nmax))
        self.plotter.Draw(gc)


if __name__ == "__main__":
    app = wx.App()
    f = MyFrame1(None)
    app.MainLoop()
