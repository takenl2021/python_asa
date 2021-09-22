#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from asapy.ASA import ASA
from asapy.init.JsonFile import JsonFile
from asapy.load.LoadJson import LoadJson
from asapy.parse.Parse import Parse
from asapy.output.Output import Output
from asapy.result.Result import Result
from openpyxl.utils.cell import column_index_from_string

from pgmpy.models import BayesianModel
from pgmpy.estimators import BayesianEstimator
import pandas as pd
import pickle

if __name__ == '__main__':
    files = JsonFile()
    dicts = LoadJson(files)
    #parser = Parse(dicts, "cabocha")
    #output = Output()
    frames = dicts.frames.frames
    columns = ['verb', 'arg', 'pos', 'rel', 'voice', 'sem', 'role']
    df = pd.DataFrame(columns=columns)
    for ins in frames['dict']:
        verb = ins['verb']
        if ins['frame']:
           for instance in ins['frame']:
                semantic = instance['semantic']
                if instance['instance']:
                    for cases in instance['instance']:
                        for case in cases['cases']:
                            df = df.append({'verb': verb, 'arg': case['arg'], 'pos': case['noun'], 'rel': case['part'], 'voice': '*', 'sem':semantic, 'role': case['semrole']}, ignore_index=True)
    model = BayesianModel([('sem','role'),('sem','voice'),('sem','verb'),('role','arg'),('role','pos'),('role','rel')])
    model.fit(df,estimator=BayesianEstimator)
    filename = 'model_json.pickle' #変えてもいい
    with open('model_json.pickle', mode='wb') as f:
            pickle.dump(model,f)    
    print('終了')
    