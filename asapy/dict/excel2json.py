"""
jsonファイルの構成
{"dict":
    [{"frame":
        [{"instance":   
            [{"cases":["weight","part","semrole","noun","arg","category"]}
            [{"cases"}]...
            "semantic"
            }
            {"instance":   
            [{"cases":["weight","part","semrole","noun","arg","category"]}
            [{"cases"}]...
            "semantic"
            }
        ]
        "verb"
    }
    ]
"""

import json 
import openpyxl
import re
import MeCab 
import CaboCha
import math

MAX_DATA_NUM = 24577

categorys_open = open('categorys.json','r')
categorys = json.load(categorys_open)

wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/動詞辞書_220711.xlsx') #should be changed
sheet = wb['dup_checked_pth'] #should be changed

def returnValue(id,data):
        obj = "A{}:BB{}".format(id,id)
        cell = data[obj]
        sentence = cell[0][39].value
        verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
        case1 = {"semrole":cell[0][4].value,"Arg":cell[0][5].value,"rel":cell[0][6].value,"surface": cell[0][7].value}
        case2 = {"semrole":cell[0][11].value,"Arg":cell[0][12].value,"rel":cell[0][13].value,"surface": cell[0][14].value}
        case3 = {"semrole":cell[0][18].value,"Arg":cell[0][19].value,"rel":cell[0][20].value,"surface": cell[0][21].value}
        case4 = {"semrole":cell[0][25].value,"Arg":cell[0][26].value,"rel":cell[0][27].value,"surface": cell[0][28].value}
        case5 = {"semrole":cell[0][32].value,"Arg":cell[0][33].value,"rel":cell[0][34].value,"surface": cell[0][35].value}
        semantic = {"1": cell[0][40].value, "2":cell[0][41].value,"3":cell[0][42].value,"4":cell[0][43].value,"5":cell[0][44].value}
        value = {"verb":verb, "sentence":sentence,"semantic":semantic, "case1":case1, "case2":case2, "case3":case3, "case4":case4, "case5":case5,}
        return value

def remove_part(surface,part):
    cp = CaboCha.Parser()
    tree = cp.parse(surface)
    pos = re.split('[*]', tree.token(0).feature)
    pos = pos[0][:-1]
    try:
        spliter = re.split('[・?]',part)
    except TypeError:
        #print("TypeERROR",surface,part, pos)
        return surface, part , pos
    for split in spliter:
        if surface != surface.rstrip(split):
            surface = surface.rstrip(split)
            part = split
    return surface , part , pos 

def block2category(surface, part):
    for ins in categorys['dict']:
        if surface in ins['noun']:
                return ins['category_name']
    return "NoData"

def make_cases(values, semantic, verb_weight, semantic_weight, index):
    case = {}
    surface , part , pos = remove_part(str(values['surface']) if values['surface'] != None else '*', values['rel'])
    category = block2category(surface,part)
    if part != None:
        weight = calc_weight(category + part, verb_weight, semantic_weight, index, semantic)
    else:
        weight = calc_weight(category, verb_weight, semantic_weight, index, semantic)
    case["noun"] = surface
    case["part"] = part
    case["category"] = category 
    case["semrole"] = values["semrole"]
    case["arg"] = values["Arg"]
    case["weight"] = weight

    return case

"""
weight is defined by tsuchiyama on page 24, 25 in this site
http://lyon.cl.cs.okayama-u.ac.jp/guestnl/meeting_data/H22/November/tsuchi/ tsichi20101112.pdf
this should not publish on github? 
"""

def calc_weight(category, verb_weight, semantic_weight, index, semantic):
    v_count = 0
    s_count = 0
    for v in verb_weight[semantic].values():
        if category in v:
            v_count += 1
    v_weight = 1 / (math.log2((len(verb_weight[semantic]) / v_count)) + 1)
    #print(v_weight)
    
    for k , v in semantic_weight.items():
        if category in v:
            s_count += 1
        if semantic == k:
            times = v[category]
    s_weight = times * ((math.log2(len(semantic_weight) / s_count)) + 1)
    weight = v_weight * s_weight
    # print("V_weight=", v_weight)
    # print("S_weight=", s_weight)
    # print("weight=", weight)
    return weight

def make_weight(values, semantic, verb_weight, semantic_weight, index):
    surface , part , pos = remove_part(str(values['surface']) if values['surface'] != None else '*', values['rel'])
    category = block2category(surface,part)
    if part != None:
        category = category + part
    if semantic not in verb_weight:
        verb_weight[semantic] = {}
    if index not in verb_weight[semantic]:
        verb_weight[semantic][index] = {}
    if category not in verb_weight[semantic][index]:
        verb_weight[semantic][index][category] = 0
    verb_weight[semantic][index][category] += 1

    if semantic not in semantic_weight:
        semantic_weight[semantic] = {}
    if category not in semantic_weight[semantic]:
        semantic_weight[semantic][category] = 0
    semantic_weight[semantic][category] += 1
    return 

#----------------main----------------

verb_list = {} #varb_list has verbkey and id which is excel row number. {"買う", [1,2,3]}
output_json = {"dict":[]}
for i in range(2,MAX_DATA_NUM):
    obj = "A{}:BB{}".format(i,i)
    cell = sheet[obj]
    verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
    if verb["verb_main"] not in verb_list:
        verb_list[verb["verb_main"]] = []
    verb_list[verb["verb_main"]].append(i)

for verb, v in verb_list.items():
    verb_weight = {}
    semantic_weight = {}
    instances = []
    #semは統一しないとまずいかも？
    for index in v:
        semantic = ""
        values = returnValue(index, sheet)
        for frame in values['semantic'].values():
            if frame != None:
                semantic += "{}-".format(frame)
            """if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)"""
        if values["case1"]["Arg"] != "false" and values["case1"]["Arg"] != None and values["case1"]["Arg"] != False:
            make_weight(values["case1"],semantic, verb_weight, semantic_weight, index)

        if values["case2"]["Arg"] != "false" and values["case2"]["Arg"] != None and values["case2"]["Arg"] != False:
            make_weight(values["case2"],semantic, verb_weight, semantic_weight, index)

        if values["case3"]["Arg"] != "false" and values["case3"]["Arg"] != None and values["case3"]["Arg"] != False:
            make_weight(values["case3"],semantic, verb_weight, semantic_weight, index)

        if values["case4"]["Arg"] != "false" and values["case4"]["Arg"] != None and values["case4"]["Arg"] != False:
            make_weight(values["case4"],semantic, verb_weight, semantic_weight, index)
            
        if values["case5"]["Arg"] != "false" and values["case5"]["Arg"] != None and values["case5"]["Arg"] != False:
            make_weight(values["case5"],semantic, verb_weight, semantic_weight, index)
    #print(verb_weight)
    #print(semantic_weight)

    for index in v:
        cases = []
        instance = {"instance":[],"semantic": ""}
        values = returnValue(index, sheet)
        semantic = ""
        for frame in values['semantic'].values():
            flg = False
            if frame != None:
                semantic += "{}-".format(frame)
            """if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)"""
        if values["case1"]["Arg"] != "false" and values["case1"]["Arg"] != None and values["case1"]["Arg"] != False:
            case = make_cases(values["case1"], semantic, verb_weight, semantic_weight, index)
            cases.append(case)

        if values["case2"]["Arg"] != "false" and values["case2"]["Arg"] != None and values["case2"]["Arg"] != False:
            case = make_cases(values["case2"], semantic, verb_weight, semantic_weight, index)
            cases.append(case)

        if values["case3"]["Arg"] != "false" and values["case3"]["Arg"] != None and values["case3"]["Arg"] != False:
            case = make_cases(values["case3"], semantic, verb_weight, semantic_weight, index)
            cases.append(case)

        if values["case4"]["Arg"] != "false" and values["case4"]["Arg"] != None and values["case4"]["Arg"] != False:
            case = make_cases(values["case4"], semantic, verb_weight, semantic_weight, index)
            cases.append(case)
            
        if values["case5"]["Arg"] != "false" and values["case5"]["Arg"] != None and values["case5"]["Arg"] != False:
            case = make_cases(values["case5"], semantic, verb_weight, semantic_weight, index)
            cases.append(case)        
        cases_json = {"cases": cases}
        for item in instances:
            if item["semantic"] == semantic:
                item["instance"].append(cases_json)
                flg = True
        if flg == False:
            instance["semantic"] = semantic
            instance["instance"].append(cases_json)
            instances.append(instance)
    frame_json = {"frame":instances, "verb": verb}
    output_json["dict"].append(frame_json)
print(output_json)

with open ("excel2json.json", "w") as f:
    json.dump(output_json, f, ensure_ascii=False)

