from openpyxl.utils.cell import column_index_from_string
import pandas as pd
import pickle
import openpyxl
import re
import MeCab 
import CaboCha
import json

#Excelのデータ読み込み
def returnValue(id,data):
        obj = "A{}:BB{}".format(id,id)
        cell = data[obj]
        sentence = cell[0][39].value
        verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
        case1 = {"role":cell[0][4].value,"arg":cell[0][5].value,"rel":cell[0][6].value,"surface": cell[0][7].value}
        case2 = {"role":cell[0][11].value,"arg":cell[0][12].value,"rel":cell[0][13].value,"surface": cell[0][14].value}
        case3 = {"role":cell[0][18].value,"arg":cell[0][19].value,"rel":cell[0][20].value,"surface": cell[0][21].value}
        case4 = {"role":cell[0][25].value,"arg":cell[0][26].value,"rel":cell[0][27].value,"surface": cell[0][28].value}
        case5 = {"role":cell[0][32].value,"arg":cell[0][33].value,"rel":cell[0][34].value,"surface": cell[0][35].value}
        semantic = {"1": cell[0][40].value, "2":cell[0][41].value,"3":cell[0][42].value,"4":cell[0][43].value,"5":cell[0][44].value}
        frame_id = cell[0][45].value
        value = {"verb":verb, "sentence":sentence,"semantic":semantic, "case1":case1,"case2":case2,"case3":case3,"case4":case4,"case5":case5,"frame_id":frame_id}
        return value

#表層格から助詞，表層を取り出す
def remove_part(surface,part):
    cp = CaboCha.Parser()
    tree = cp.parse(surface)
    pos = re.split('[*]', tree.token(0).feature)
    pos = pos[0][:-1]
    try:
        spliter = re.split('[・?]',part)
    except TypeError: ##原因は助詞がないこと = partがNone
        #print("TypeERROR",surface,part, pos)
        return surface, part , pos
    for split in spliter:
        if surface != surface.rstrip(split):
            surface = surface.rstrip(split)
            part = split
    #print(surface,part, pos)
    return surface , part , pos 


#態の判定
def parseVoice(sentence):
    parser = CaboCha.Parser()
    voice = ""
    pos = ""
    if sentence:
        tree =  parser.parse(sentence)
        line_list = tree.toString(CaboCha.FORMAT_LATTICE).split("\n")
        for line in line_list:
            if line == "EOS":
                break
            if line.startswith("* "):
                continue
            else:

                div1 = line.split("\t")
                div2 = div1[1].split(",")
                if div2[0] != "*":
                    pos = pos + div2[0]
                if div2[1] != "*":
                    pos = pos + "," + div2[1]
                if div2[2] != "*":
                    pos = pos + "," + div2[2]
                if div2[3] != "*":
                    pos = pos + "," + div2[3]
            #if re.search(r"れる|られる", div2[6]) and re.search(r"動詞,接尾", pos):
            if (div2[6] == "れる" or div2[6] == "られる") and \
                re.search(r"動詞,接尾", pos):
                voice = "PASSIVE"
            elif div2[6] == "できる" and re.search(r"動詞,自立", pos):
                voice = "POTENTIAL"
            elif (div2[6] in ["せる", "させる"] and re.search(r"動詞,接尾", pos)) or \
                (div2[6] == "もらう" or div2[6] == "いただく") and \
                re.search(r"動詞,非自立", pos):
                voice = "CAUSATIVE"
    if not voice:
        voice = "ACTIVE"
    return voice

if __name__ == '__main__':
    #DATA_NUM = 24130 #旧データ
    DATA_NUM = 24577

    #Excelからデータ読み込み
    #旧データ
    #wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/pth20210305.xlsx') #should be changed
    #sheet1 = wb['pth20210305-sjis']

    wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/動詞辞書_220711.xlsx') #should be changed
    sheet1 = wb['dup_checked_pth']


    sem_mapping = {}
    verb_mapping = {}
    role_mapping = {}
    surface_mapping = {}
    rel_mapping = {}
    pos_mapping = {}
    arg_mapping = {}
    voice_mapping = {}

    verb_index = 0
    role_index = 0
    surface_index = 0
    rel_index = 0
    pos_index = 0
    arg_index = 0
    voice_index = 0

    output_json = {}

    for i in range(2,DATA_NUM):
        values = returnValue(i,sheet1)
        semantic = ""
        voice = ""
        frame_id = values["frame_id"]

        if values['sentence'] == None:
            continue

        for frame in values['semantic'].values():
            if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)
# 態のマッピング
        voice = parseVoice(values["sentence"])
        if voice not in voice_mapping.keys():
            voice_mapping.setdefault(voice, voice_index)
            voice_index +=1 
# 概念フレームのマッピング 概念フレームのハイフン統一が必要                
        sem_mapping.setdefault(semantic, frame_id)
        if values['verb']['verb_main'] not in verb_mapping.keys():
            verb_mapping.setdefault(values['verb']['verb_main'], verb_index)
            verb_index += 1

        if values['sentence'] == None:
                continue
        else:
            if values["case1"]["arg"] != "false" and values["case1"]["arg"] != None and values["case1"]["arg"] != False:
                surface , part , pos = remove_part(str(values["case1"]['surface']) if values["case1"]['surface'] != None else '*', values["case1"]['rel'])
                if surface not in surface_mapping.keys():
                    surface_mapping.setdefault(surface, surface_index)
                    surface_index +=1 
                if part not in rel_mapping.keys():
                    rel_mapping.setdefault(part, rel_index)
                    rel_index +=1
                if pos not in pos_mapping.keys():
                    pos_mapping.setdefault(pos, pos_index)
                    pos_index +=1  
                if values["case1"]["role"] not in role_mapping.keys():
                    role_mapping.setdefault(values["case1"]["role"], role_index)
                    role_index +=1  
                if values["case1"]["arg"] not in arg_mapping.keys():
                    arg_mapping.setdefault(values["case1"]["arg"], arg_index)
                    arg_index +=1  

            if values["case2"]["arg"] != "false" and values["case2"]["arg"] != None and values["case2"]["arg"] != False:
                surface , part , pos = remove_part(str(values["case2"]['surface']) if values["case2"]['surface'] != None else '*', values["case2"]['rel'])
                if surface not in surface_mapping.keys():
                    surface_mapping.setdefault(surface, surface_index)
                    surface_index +=1 
                if part not in rel_mapping.keys():
                    rel_mapping.setdefault(part, rel_index)
                    rel_index +=1
                if pos not in pos_mapping.keys():
                    pos_mapping.setdefault(pos, pos_index)
                    pos_index +=1  
                if values["case2"]["role"] not in role_mapping.keys():
                    role_mapping.setdefault(values["case2"]["role"], role_index)
                    role_index +=1  
                if values["case2"]["arg"] not in arg_mapping.keys():
                    arg_mapping.setdefault(values["case2"]["arg"], arg_index)
                    arg_index +=1  

            if values["case3"]["arg"] != "false" and values["case3"]["arg"] != None and values["case3"]["arg"] != False:
                surface , part , pos = remove_part(str(values["case3"]['surface']) if values["case3"]['surface'] != None else '*', values["case3"]['rel'])
                if surface not in surface_mapping.keys():
                    surface_mapping.setdefault(surface, surface_index)
                    surface_index +=1 
                if part not in rel_mapping.keys():
                    rel_mapping.setdefault(part, rel_index)
                    rel_index +=1
                if pos not in pos_mapping.keys():
                    pos_mapping.setdefault(pos, pos_index)
                    pos_index +=1  
                if values["case3"]["role"] not in role_mapping.keys():
                    role_mapping.setdefault(values["case3"]["role"], role_index)
                    role_index +=1  
                if values["case3"]["arg"] not in arg_mapping.keys():
                    arg_mapping.setdefault(values["case3"]["arg"], arg_index)
                    arg_index +=1  

            if values["case4"]["arg"] != "false" and values["case4"]["arg"] != None and values["case4"]["arg"] != False:
                surface , part , pos = remove_part(str(values["case4"]['surface']) if values["case4"]['surface'] != None else '*', values["case4"]['rel'])
                if surface not in surface_mapping.keys():
                    surface_mapping.setdefault(surface, surface_index)
                    surface_index +=1 
                if part not in rel_mapping.keys():
                    rel_mapping.setdefault(part, rel_index)
                    rel_index +=1
                if pos not in pos_mapping.keys():
                    pos_mapping.setdefault(pos, pos_index)
                    pos_index +=1  
                if values["case4"]["role"] not in role_mapping.keys():
                    role_mapping.setdefault(values["case4"]["role"], role_index)
                    role_index +=1  
                if values["case4"]["arg"] not in arg_mapping.keys():
                    arg_mapping.setdefault(values["case4"]["arg"], arg_index)
                    arg_index +=1  

            if values["case5"]["arg"] != "false" and values["case5"]["arg"] != None and values["case5"]["arg"] != False:
                surface , part , pos = remove_part(str(values["case5"]['surface']) if values["case5"]['surface'] != None else '*', values["case5"]['rel'])
                if surface not in surface_mapping.keys():
                    surface_mapping.setdefault(surface, surface_index)
                    surface_index +=1 
                if part not in rel_mapping.keys():
                    rel_mapping.setdefault(part, rel_index)
                    rel_index +=1
                if pos not in pos_mapping.keys():
                    pos_mapping.setdefault(pos, pos_index)
                    pos_index +=1 
                if values["case5"]["role"] not in role_mapping.keys():
                    role_mapping.setdefault(values["case5"]["role"], role_index)
                    role_index +=1  
                if values["case5"]["arg"] not in arg_mapping.keys():
                    arg_mapping.setdefault(values["case5"]["arg"], arg_index)
                    arg_index +=1   

    #print(sem_mapping)
    #print(verb_mapping)
    #print(rel_mapping)
    #print(pos_mapping)
    #print(surface_mapping)

# すべてを一つのjson形式に集約
    output_json.setdefault("sem_mapping", sem_mapping)
    output_json.setdefault("verb_mapping", verb_mapping)
    output_json.setdefault("role_mapping", role_mapping)
    output_json.setdefault("rel_mapping", rel_mapping)
    output_json.setdefault("pos_mapping", pos_mapping)
    output_json.setdefault("surface_mapping", surface_mapping)
    output_json.setdefault("arg_mapping", pos_mapping)

    filename = 'mapping.json' #変えてもいい
    with open(filename, mode='w') as f:
            json.dump(output_json,f,ensure_ascii=False)  

    print(output_json)
    