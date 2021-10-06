#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from asapy.ASA import ASA
from openpyxl.utils.cell import column_index_from_string

from pgmpy.models import BayesianModel
from pgmpy.estimators import BayesianEstimator
import pandas as pd
import pickle
import openpyxl
import re

def returnValue(id,data):
        obj = "A{}:BB{}".format(id,id)
        cell = data[obj]
        sentence = cell[0][39].value
        verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
        case1 = {"semrole":cell[0][4].value,"Arg":cell[0][5].value,"pos":cell[0][6].value,"surface": cell[0][7].value}
        case2 = {"semrole":cell[0][11].value,"Arg":cell[0][12].value,"pos":cell[0][13].value,"surface": cell[0][14].value}
        case3 = {"semrole":cell[0][18].value,"Arg":cell[0][19].value,"pos":cell[0][20].value,"surface": cell[0][21].value}
        case4 = {"semrole":cell[0][25].value,"Arg":cell[0][26].value,"pos":cell[0][27].value,"surface": cell[0][28].value}
        case5 = {"semrole":cell[0][32].value,"Arg":cell[0][33].value,"pos":cell[0][34].value,"surface": cell[0][35].value}
        semantic = {"1": cell[0][40].value, "2":cell[0][41].value,"3":cell[0][42].value,"4":cell[0][43].value,"5":cell[0][44].value}
        value = {"verb":verb, "sentence":sentence,"semantic":semantic, "case1":case1, "case2":case2, "case3":case3, "case4":case4, "case5":case5,}
        return value

def remove_part(surface,part):
    try:
        spliter = re.split('[・?]',part)
    except TypeError:
        return surface, part
    for split in spliter:
        if surface != surface.rstrip(split):
            surface = surface.rstrip(split)
            part = split
    #print(surface,part)
    return surface , part

if __name__ == '__main__':
    DATA_NUM = 24130
    columns = ['verb', 'arg', 'pos', 'rel', 'voice', 'sem', 'role']
    wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/pth20210305.xlsx') #should be changed
    sheet = wb['pth20210305-sjis']
    df = pd.DataFrame(columns=columns)
    for i in range(2,DATA_NUM): #2
        values = returnValue(i,sheet)
        semantic = ""
        for frame in values['semantic'].values():
            if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)
        if values['sentence'] == None:
                continue
        else:
            if values["case1"]["Arg"] != "false" and values["case1"]["Arg"] != None and values["case1"]["Arg"] != False:
                surface , part = remove_part((values["case1"]['surface']) if values["case1"]['surface'] != None else '*', values["case1"]['pos'])
                df = df.append({'verb': values["verb"]["verb_main"], 'arg': values["case1"]["Arg"], 'pos': str(surface), 'rel': part, 'voice': '*', 'sem':semantic, 'role': values["case1"]["semrole"]}, ignore_index=True)
            if values["case2"]["Arg"] != "false" and values["case2"]["Arg"] != None and values["case2"]["Arg"] != False:
                surface , part = remove_part((values["case2"]['surface']) if values["case2"]['surface'] != None else '*', values["case2"]['pos'])
                df = df.append({'verb': values["verb"]["verb_main"], 'arg': values["case2"]["Arg"], 'pos': str(surface), 'rel': part, 'voice': '*', 'sem':semantic, 'role': values["case2"]["semrole"]}, ignore_index=True)
            if values["case3"]["Arg"] != "false" and values["case3"]["Arg"] != None and values["case3"]["Arg"] != False:
                surface , part = remove_part((values["case3"]['surface']) if values["case3"]['surface'] != None else '*', values["case3"]['pos'])
                df = df.append({'verb': values["verb"]["verb_main"], 'arg': values["case3"]["Arg"], 'pos': str(surface), 'rel': part, 'voice': '*', 'sem':semantic, 'role': values["case3"]["semrole"]}, ignore_index=True)
            if values["case4"]["Arg"] != "false" and values["case4"]["Arg"] != None and values["case4"]["Arg"] != False:
                surface , part = remove_part((values["case4"]['surface']) if values["case4"]['surface'] != None else '*', values["case4"]['pos'])
                df = df.append({'verb': values["verb"]["verb_main"], 'arg': values["case4"]["Arg"], 'pos': str(surface), 'rel': part, 'voice': '*', 'sem':semantic, 'role': values["case4"]["semrole"]}, ignore_index=True)
            if values["case5"]["Arg"] != "false" and values["case5"]["Arg"] != None and values["case5"]["Arg"] != False:
                surface , part = remove_part((values["case5"]['surface']) if values["case5"]['surface'] != None else '*', values["case5"]['pos'])
                df = df.append({'verb': values["verb"]["verb_main"], 'arg': values["case5"]["Arg"], 'pos': str(surface), 'rel': part, 'voice': '*', 'sem':semantic, 'role': values["case5"]["semrole"]}, ignore_index=True)

    model = BayesianModel([('sem','role'),('sem','voice'),('sem','verb'),('role','arg'),('role','pos'),('role','rel')])
    model.fit(df,estimator=BayesianEstimator)
    filename = 'model_pth.pickle' #変えてもいい
    with open('model_pth.pickle', mode='wb') as f:
            pickle.dump(model,f)    
    print('終了')
    #TODO 助詞を文字列マッチで消す

