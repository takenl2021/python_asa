from asapy.result.Result import Result
import openpyxl
import json
from ASA_pgmpy import ASA
import time

class Evaluate():

    def __init__(self) -> None:
        self.number = 24130
        self.sheet = self.__openSheet()
        self.SemanticCount = {'true': 0, 'falsePositive' :0, 'falseNegative' : 0}
        self.ArgCount = {'true': 0, 'falsePositive' : 0, 'falseNegative' :0}
        self.SemroleCount = {'true': 0, 'falsePositive': 0, 'falseNegative' :0}
        self.asa = ASA()

    def calculate(self):
        print("20000万件実行中")
        #for i in range(2,24130):
        #10360あたりのデータが壊れている
        output_json = []
        for i in range(2,self.number): #2~24130
            print(i)
            correct_json = {'output': {},'correct':[]}
            values = self.returnValue(i)
            if values['sentence'] == None:
                continue
            else:
                self.asa.parse(values['sentence'])
                result = self.asa.result

                for chunk in result.chunks:
                    correct_chunk = self.chunkType(chunk, values)
                    if correct_chunk != {}:
                        correct_json['correct'].append(correct_chunk)
                if correct_json['correct'] != []:
                    result_json = self.outputJson(result)
                    correct_json['output'] = result_json
        calc_values = self.calculate_value()
        self.outputResult(calc_values)


    def __openSheet(self):
        wb = openpyxl.load_workbook('data/pth20210305.xlsx')
        sheet = wb['pth20210305-sjis']
        return sheet

    def returnValue(self, id):
        obj = "A{}:BB{}".format(id,id)
        cell = self.sheet[obj]
        sentence = cell[0][39].value
        verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
        case1 = {"semrole":cell[0][4].value,"Arg":cell[0][5].value,"表層格":cell[0][6].value,"surface": cell[0][7].value,"格要素":cell[0][8].value,"フレーム変数": cell[0][9].value,"Filled": cell[0][10].value}
        case2 = {"semrole":cell[0][11].value,"Arg":cell[0][12].value,"表層格":cell[0][13].value,"surface": cell[0][14].value,"格要素":cell[0][15].value,"フレーム変数": cell[0][16].value,"Filled": cell[0][17].value}
        case3 = {"semrole":cell[0][18].value,"Arg":cell[0][19].value,"表層格":cell[0][20].value,"surface": cell[0][21].value,"格要素":cell[0][22].value,"フレーム変数": cell[0][23].value,"Filled": cell[0][24].value}
        case4 = {"semrole":cell[0][25].value,"Arg":cell[0][26].value,"表層格":cell[0][27].value,"surface": cell[0][28].value,"格要素":cell[0][29].value,"フレーム変数": cell[0][30].value,"Filled": cell[0][31].value}
        case5 = {"semrole":cell[0][32].value,"Arg":cell[0][33].value,"表層格":cell[0][34].value,"surface": cell[0][35].value,"格要素":cell[0][36].value,"フレーム変数": cell[0][37].value,"Filled": cell[0][38].value}
        semantic = {"1": cell[0][40].value, "2":cell[0][41].value,"3":cell[0][42].value,"4":cell[0][43].value,"5":cell[0][44].value}
        value = {"verb":verb, "sentence":sentence,"semantic":semantic, "case1":case1, "case2":case2, "case3":case3, "case4":case4, "case5":case5,}
        return value

            #深層系 = semrole
            #格1 = 4~10
            #格2 = 11~17
            #格3 = 18~24
            #格4 = 25~31
            #格5 = 32~38
            #例文 = 39
    
    def chunkType(self, chunk, values):
        correct_chunk = {}
        if chunk.ctype == "elem":
            correct_chunk = self.compareElem(chunk, values)
        if chunk.ctype == "adjective":
            correct_chunk = self.adjective(chunk, values)
        if chunk.ctype == "verb":
            correct_chunk = self.compareVerb(chunk, values)
        return correct_chunk

    def compareElem(self, chunk, values):
        correct_chunk = {}
        if chunk.arg:
            if chunk.surface in values['case1'].values():
                if chunk.arg[0] == values['case1']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case1']['Arg']
                    correct_chunk['surface'] = values['case1']['surface']
            elif chunk.surface in values['case2'].values():
                if chunk.arg[0] == values['case2']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case2']['Arg']
                    correct_chunk['surface'] = values['case2']['surface']
            elif chunk.surface in values['case3'].values():
                if chunk.arg[0] == values['case3']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case3']['Arg']
                    correct_chunk['surface'] = values['case3']['surface']
            elif chunk.surface in values['case4'].values():
                if chunk.arg[0] == values['case4']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case4']['Arg']
                    correct_chunk['surface'] = values['case4']['surface']
            elif chunk.surface in values['case5'].values():
                if chunk.arg[0] == values['case5']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case5']['Arg']
                    correct_chunk['surface'] = values['case5']['surface']
            else:
                #print("Argはあるけど正しく振られてない(fp)") #tp = FALSE retrieved = TRUE,FALSE
                self.ArgCount['falsePositive'] += 1
        else:
            self.ArgCount['falseNegative'] += 1

        if chunk.semrole:
            if chunk.surface in values['case1'].values():
                if chunk.semrole[0] == values['case1']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case1']['semrole']
                    correct_chunk['surface'] = values['case1']['surface']
            elif chunk.surface in values['case2'].values():
                if chunk.semrole[0] == values['case2']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case2']['semrole']
                    correct_chunk['surface'] = values['case2']['surface']
            elif chunk.surface in values['case3'].values():
                if chunk.semrole[0] == values['case3']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case3']['semrole']
                    correct_chunk['surface'] = values['case3']['surface']
            elif chunk.surface in values['case4'].values():
                if chunk.semrole[0] == values['case4']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case4']['semrole']
                    correct_chunk['surface'] = values['case4']['surface']
            elif chunk.surface in values['case5'].values():
                if chunk.semrole[0] == values['case5']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case5']['semrole']
                    correct_chunk['surface'] = values['case5']['surface']
            else:
                #print("Semはあるけど正しく振られてない(fp)") #tp = FALSE retrieved = TRUE,FALSE
                self.SemroleCount['falsePositive'] += 1
        else:
            self.SemroleCount['falseNegative'] += 1
        
        return correct_chunk

    def compareVerb(self, chunk, values):
        string_read = ""
        semantic = ""
        correct_chunk = {}
        
        for frame in values['semantic'].values():
            if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)
        for morph in chunk.morphs:
            string_read += morph.read

        if chunk.main:
            if chunk.main == values['verb']['verb_main'] and string_read == values['verb']['verb_read']:       
                if chunk.semantic:
                    if chunk.semantic == semantic:
                        self.SemanticCount['true'] += 1
                    else:
                        self.SemanticCount['falsePositive'] += 1
                        correct_chunk['semantic'] = semantic
                else:
                    self.SemanticCount['falseNegative'] += 1
                    correct_chunk['falseNegative'] = "FALSENEGATIVE"
            #else:
                #形態素解析のミス？
                #self.SemanticCount['falsePositive'] += 1
                #correct_chunk['verb_main'] = values['verb']['verb_main']
                #correct_chunk['verb_read'] = values['verb']['verb_read']

        return correct_chunk

    def returnCaseValue(self,chunk,case,tp):
            if chunk.arg[0] in case.values():
                if chunk.surface in case.values() and chunk.semrole[0] in case.values() and chunk.part in case.values(): #partはいらない
                    value = {"Arg":None,"surface":None,"semrole":None,"part":None,"tp":tp}
                    return value
                else:
                    tp = False
                    value = {"Arg":case['Arg'],"surface":case["事例"],"semrole":case["深層格"],"part":case["表層格"],"tp":False}
                    return value

    def adjective(self, chunk, values):
        correct_chunk = {}        
        string_read = ""
        semantic = ""
        
        for frame in values['semantic'].values():
            if frame == None:
                semantic += "-"
            else:
                semantic += "{}-".format(frame)
        for morph in chunk.morphs:
            string_read += morph.read

        if chunk.semantic:
            if chunk.main:
                if chunk.main == values['verb']['verb_main'] and string_read == values['verb']['verb_read']:       
                    if chunk.semantic == semantic:
                        self.SemanticCount['true'] += 1
                        return correct_chunk
                    else:
                        self.SemanticCount['falsePositive'] += 1
                        correct_chunk['semantic'] = semantic
                        return correct_chunk
                else:
                    self.SemanticCount['falseNegative'] += 1
                    correct_chunk['falseNegative'] = "FALSENEGATIVE"
                    return correct_chunk
            else:
                return correct_chunk
                #形態素解析のミス？
                #self.SemanticCount['falsePositive'] += 1
                #correct_chunk['verb_main'] = values['verb']['verb_main']
                #correct_chunk['verb_read'] = values['verb']['verb_read']

        if chunk.arg:
            if chunk.surface in values['case1'].values():
                if chunk.arg[0] == values['case1']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case1']['Arg']
                    correct_chunk['surface'] = values['case1']['surface']
            elif chunk.surface in values['case2'].values():
                if chunk.arg[0] == values['case2']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case2']['Arg']
                    correct_chunk['surface'] = values['case2']['surface']
            elif chunk.surface in values['case3'].values():
                if chunk.arg[0] == values['case3']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case3']['Arg']
                    correct_chunk['surface'] = values['case3']['surface']
            elif chunk.surface in values['case4'].values():
                if chunk.arg[0] == values['case4']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case4']['Arg']
                    correct_chunk['surface'] = values['case4']['surface']
            elif chunk.surface in values['case5'].values():
                if chunk.arg[0] == values['case5']['Arg']:
                    self.ArgCount['true'] += 1
                else:
                    self.ArgCount['falsePositive'] += 1
                    correct_chunk['Arg'] = values['case5']['Arg']
                    correct_chunk['surface'] = values['case5']['surface']
            else:
                #print("Argはあるけど正しく振られてない(fp)") #tp = FALSE retrieved = TRUE,FALSE
                self.ArgCount['falsePositive'] += 1
        else:
            self.ArgCount['falseNegative'] += 1
            correct_chunk['falseNegative'] = "FALSENEGATIVE"

        if chunk.semrole:
            if chunk.surface in values['case1'].values():
                if chunk.semrole[0] == values['case1']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case1']['semrole']
                    correct_chunk['surface'] = values['case1']['surface']
            elif chunk.surface in values['case2'].values():
                if chunk.semrole[0] == values['case2']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case2']['semrole']
                    correct_chunk['surface'] = values['case2']['surface']
            elif chunk.surface in values['case3'].values():
                if chunk.semrole[0] == values['case3']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case3']['semrole']
                    correct_chunk['surface'] = values['case3']['surface']
            elif chunk.surface in values['case4'].values():
                if chunk.semrole[0] == values['case4']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case4']['semrole']
                    correct_chunk['surface'] = values['case4']['surface']
            elif chunk.surface in values['case5'].values():
                if chunk.semrole[0] == values['case5']['semrole']:
                    self.SemroleCount['true'] += 1
                else:
                    self.SemroleCount['falsePositive'] += 1
                    correct_chunk['semrole'] = values['case5']['semrole']
                    correct_chunk['surface'] = values['case5']['surface']
            else:
                #print("Semはあるけど正しく振られてない(fp)") #tp = FALSE retrieved = TRUE,FALSE
                self.SemroleCount['falsePositive'] += 1
        else:
            self.SemroleCount['falseNegative'] += 1
            correct_chunk['falseNegative'] = "FALSENEGATIVE"

        return correct_chunk

# precision適合率 = tp / (tp + fp) https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/precision.html
# recall再現率 = tp / (tp+fn) https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/recall.html
# F-value = 2*precision*recall /(precision + recall)  https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/tpfptnfn.html

    def calculate_value(self):
        Semantic_precision = self.SemanticCount['true'] / (self.SemanticCount['true'] + self.SemanticCount['falsePositive'])
        Semantic_recall = self.SemanticCount['true'] / (self.SemanticCount['true'] + self.SemanticCount['falseNegative'])
        Semantic_F_value = 2 * Semantic_precision * Semantic_recall / (Semantic_precision + Semantic_recall)
        Semrole_precision = self.SemroleCount['true'] / (self.SemroleCount['true'] + self.SemroleCount['falsePositive'])
        Semrole_recall = self.SemroleCount['true'] / (self.SemroleCount['true'] + self.SemroleCount['falseNegative'])
        Semrole_F_value = 2 * Semrole_precision * Semrole_recall / (Semrole_precision + Semrole_recall)
        Arg_precision = self.ArgCount['true'] / (self.ArgCount['true'] + self.ArgCount['falsePositive'])
        Arg_recall = self.ArgCount['true'] / (self.ArgCount['true'] + self.ArgCount['falseNegative'])
        Arg_F_value = 2 * Arg_precision * Arg_recall / (Arg_precision + Arg_recall)
        return {"precision": {"semantic":Semantic_precision,"semrole":Semrole_precision,"arg":Arg_precision}, "recall": {"semantic":Semantic_recall,"semrole":Semrole_recall,"arg":Arg_recall}, "F_value":{"semantic":Semantic_F_value,"semrole":Semrole_F_value,"arg":Arg_F_value}}

    def outputResult(self,calc_values):
        print("全語義: " + str(self.SemanticCount['true'] + self.SemanticCount['falsePositive'] + self.SemanticCount['falseNegative']))
        print(" 語義の一致: " + str(self.SemanticCount["true"]))
        print(" 語義の不一致: " + str(self.SemanticCount["falsePositive"]))
        print(" 取れなかった動詞: " + str(self.SemanticCount["falseNegative"]))
        print("Semantic_precision\t" + str(calc_values['precision']['semantic'] * 100) + "%")
        print("Semantic_recall\t" + str(calc_values['recall']['semantic'] * 100) + "%")
        print("Semantic_F_value\t" , calc_values['F_value']['semantic'] * 100 , "%")
        print()
        print("全意味役割: " + str(self.SemroleCount['true'] + self.SemroleCount['falsePositive'] + self.SemroleCount['falseNegative']))
        print(" 意味役割の一致: " + str(self.SemroleCount["true"]))
        print(" 意味役割の不一致: " + str(self.SemroleCount["falsePositive"]))
        print(" 取れなかったchunk: " + str(self.SemroleCount["falseNegative"]))
        print("Semrole_presicion\t" + str(calc_values['precision']['semrole'] * 100) + "%")
        print("Semrole_recall\t" + str(calc_values['recall']['semrole'] * 100) + "%")
        print("Semrole_F_value\t" , calc_values['F_value']['semrole'] * 100 , "%")
        print()
        print("全Arg: " + str(self.ArgCount['true'] + self.ArgCount['falsePositive'] + self.ArgCount['falseNegative']))
        print(" Argの一致: " + str(self.ArgCount["true"]))
        print(" Argの不一致: " + str(self.ArgCount["falsePositive"]))
        print(" 取れなかったArg: " + str(self.ArgCount["falseNegative"]))
        print("Arg_presicion\t" + str(calc_values['precision']['arg'] * 100) + "%")
        print("Arg_recall\t" + str(calc_values['recall']['arg'] * 100) + "%")
        print("Arg_F_value\t" , calc_values['F_value']['arg'] * 100 , "%")
        print()
        print("Semantic" + str(self.SemanticCount))
        print("Semrole" + str(self.SemroleCount))
        print("Arg" + str(self.ArgCount))

    def outputJsonfile(self,correct_json, result_json, filename):
            emptyList = [result_json, correct_json]
            with open(filename,'w') as f: #example_number(1,2)
                json.dump(emptyList,f,sort_keys=True,indent=4,ensure_ascii=False)
    
    def outputJson(self, result: Result) -> None:
        result_json = {'chunks': [], 'surface': result.surface}
        for chunk in result.chunks:
            chunk_dic = {}
            chunk_dic['id'] = chunk.id
            chunk_dic['surface'] = chunk.surface
            chunk_dic['link'] = chunk.link
            chunk_dic['head'] = chunk.head
            chunk_dic['Arg'] = chunk.arg #追加した
            chunk_dic['fanc'] = chunk.fanc
            chunk_dic['score'] = chunk.score
            if chunk.modifiedchunks:
                chunk_dic['modified'] = []
                for mchunk in chunk.modifiedchunks:
                    chunk_dic['modified'].append(mchunk.id)
            chunk_dic['type'] = chunk.ctype
            chunk_dic['main'] = chunk.main
            if chunk.part: chunk_dic['part'] = chunk.part
            if chunk.tense: chunk_dic['tense'] = chunk.tense
            if chunk.voice: chunk_dic['voice'] = chunk.voice
            if chunk.polarity: chunk_dic['polarity'] = chunk.polarity
            if chunk.sentelem: chunk_dic['sentelem'] = chunk.sentelem
            if chunk.mood: chunk_dic['mood'] = chunk.mood
            if chunk.semantic: chunk_dic['semantic'] = chunk.semantic
            if chunk.modifiedchunks:
                chunk_dic['frames'] = []
                for mchunk in chunk.modifiedchunks:
                    frame_dic = {}
                    frame_dic['id'] = mchunk.id
                    frame_dic['semrole'] = '|'.join(mchunk.semrole)
                    chunk_dic['frames'].append(frame_dic)
            if chunk.semrole: chunk_dic['semrole'] = '|'.join(chunk.semrole)
            if chunk.adjunct: chunk_dic['adjunct'] = chunk.adjunct
            if chunk.category: chunk_dic['category'] = chunk.category

            chunk_dic['morphs'] = []
            for morph in chunk.morphs:
                morph_dic = {}
                morph_dic['id'] = morph.id
                morph_dic['surface'] = morph.surface
                morph_dic['pos'] = morph.pos
                morph_dic['cform'] = morph.cform
                morph_dic['ctype'] = morph.ctype
                morph_dic['base'] = morph.base
                morph_dic['read'] = morph.read
                morph_dic['pos'] = morph.pos
                if morph.forms:
                    morph_dic['forms'] = []
                    for form in morph.forms:
                        morph_dic['forms'].append(form)
                chunk_dic['morphs'].append(morph_dic)
            result_json['chunks'].append(chunk_dic)
        return result_json

#-----------以前のやつ--------
# 全語義: 21878
#  語義の一致: 19061
#  語義の不一致: 1759
#  取れなかった動詞: 1058
# Semantic_precision	91.55139289145053%
# Semantic_recall	94.74128932849545%
# Semantic_F_value	 93.11903075307164 %

# 全意味役割: 42430
#  意味役割の一致: 30546
#  意味役割の不一致: 6629
#  取れなかったchunk: 5255
# Semrole_presicion	82.16812373907196%
# Semrole_recall	85.32163906036145%
# Semrole_F_value	 83.71519403639553 %

# 全Arg: 42430
#  Argの一致: 26565
#  Argの不一致: 10463
#  取れなかったArg: 5402
# Arg_presicion	71.74300529329156%
# Arg_recall	83.10132323959083%
# Arg_F_value	 77.00558011450104 %

# Semantic{'true': 19061, 'falsePositive': 1759, 'falseNegative': 1058}
# Semrole{'true': 30546, 'falsePositive': 6629, 'falseNegative': 5255}
# Arg{'true': 26565, 'falsePositive': 10463, 'falseNegative': 5402}
# elapsed_time:355.7454414367676[sec]

#--------------VOICE実装後 ve------
# 全語義: 21393
#  語義の一致: 16111
#  語義の不一致: 4582
#  取れなかった動詞: 700
# Semantic_precision	77.85724641183009%
# Semantic_recall	95.83605972280054%
# Semantic_F_value	 85.91616894197952 %

# 全意味役割: 42915
#  意味役割の一致: 31987
#  意味役割の不一致: 5492
#  取れなかったchunk: 5436
# Semrole_presicion	85.34646068465007%
# Semrole_recall	85.47417363653368%
# Semrole_F_value	 85.4102694187071 %

# 全Arg: 42915
#  Argの一致: 31796
#  Argの不一致: 5683
#  取れなかったArg: 5436
# Arg_presicion	84.83684196483364%
# Arg_recall	85.39965620971208%
# Arg_F_value	 85.11731873485833 %

# Semantic{'true': 16111, 'falsePositive': 4582, 'falseNegative': 700}
# Semrole{'true': 31987, 'falsePositive': 5492, 'falseNegative': 5436}
# Arg{'true': 31796, 'falsePositive': 5683, 'falseNegative': 5436}
# elapsed_time:41592.86124253273[sec]

#-----------------CPD-----
# 全語義: 21640
#  語義の一致: 15813
#  語義の不一致: 5238
#  取れなかった動詞: 589
# Semantic_precision	75.11757161179992%
# Semantic_recall	96.40897451530302%
# Semantic_F_value	 84.44183376498545 %

# 全意味役割: 42668
#  意味役割の一致: 31099
#  意味役割の不一致: 9014
#  取れなかったchunk: 2555
# Semrole_presicion	77.52848203824196%
# Semrole_recall	92.40803470612707%
# Semrole_F_value	 84.316835441322 %

# 全Arg: 42668
#  Argの一致: 26992
#  Argの不一致: 13121
#  取れなかったArg: 2555
# Arg_presicion	67.28990601550619%
# Arg_recall	91.35276000947643%
# Arg_F_value	 77.49641113982199 %

# Semantic{'true': 15813, 'falsePositive': 5238, 'falseNegative': 589}
# Semrole{'true': 31099, 'falsePositive': 9014, 'falseNegative': 2555}
# Arg{'true': 26992, 'falsePositive': 13121, 'falseNegative': 2555}
# elapsed_time:6397.030241012573[sec]




