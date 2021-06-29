#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from ASA import ASA
from asapy.init.JsonFile import JsonFile
from asapy.load.LoadJson import LoadJson
from asapy.parse.Parse import Parse
from asapy.output.Output import Output
from asapy.result.Result import Result

from pgmpy.models import BayesianModel
import pandas as pd
import pickle

if __name__ == '__main__':
    files = JsonFile()
    dicts = LoadJson(files)
    parser = Parse(dicts, "cabocha")
    output = Output()
    frames = dicts.frames.frames

    with open('model_json.pickle', mode='rb') as f:  # with構文でファイルパスとバイナリ読み込みモードを設定
        model = pickle.load(f)                  # オブジェクトをデシリアライズ
    
    print(model.get_cpds('sem'))
    while(True):
        inp = input()
        if not inp:
            break
        result = parser.parse(inp)
        output.outputAll(result)
    print('終了')
#TODO modelを作る。
#modelを保存しておく.保存の仕方