from asapy.result.Result import Result
import openpyxl
import json
from ASA import ASA

class Evaluate():

    def __init__(self) -> None:
        self.number = 24130
        self.data = self.__openSheet()
        self.totalTp = 0
        self.totalFp = 0
        self.totalFn = 0
        self.totalNn = 0
        self.asa = ASA()

    def calculate(self):
        #for i in range(2,24130):
        #10360あたりのデータが壊れている
        for i in range(2,19):
            correct_json = {'correct':[]}
            values = self.returnValue(i)
            if values['sentence'] == None:
                continue
            else:
                print("aaaaaaaaaaaa")
                self.asa.parse(values['sentence'])
                print("bbbb")
                result = self.asa.result
                
                tp = True
                fn = False

                for chunk in result.chunks:
                    correct_chunk = self.chunkType(chunk, values, tp, fn)
                    tp = correct_chunk['tp']
                    fn = correct_chunk['fn']
                    #print(correct_chunk)
                    correct_json['correct'].append(correct_chunk)
                self.sumup(tp,fn)
                # result_json = self.outputJson(result)
                # filename =  "diff/example_{}.json".format(i-1)
                # self.outputJsonfile(correct_json, result_json,filename, tp, fn)
        precision,recall,F_value = self.calculate_value()
        self.output(precision, recall, F_value)


    def __openSheet(self):
        wb = openpyxl.load_workbook('data/pth20210305.xlsx')
        sheet = wb['pth20210305-sjis']
        return sheet

    def returnValue(self, id):
        obj = "A{}:BB{}".format(id,id)
        cell = self.data[obj]
        sentence = cell[0][39].value
        verb = {"verb_main":cell[0][2].value,"verb_read":cell[0][3].value}
        case1 = {"深層格":cell[0][4].value,"Arg":cell[0][5].value,"表層格":cell[0][6].value,"事例": cell[0][7].value,"格要素":cell[0][8].value,"フレーム変数": cell[0][9].value,"Filled": cell[0][10].value}
        case2 = {"深層格":cell[0][11].value,"Arg":cell[0][12].value,"表層格":cell[0][13].value,"事例": cell[0][14].value,"格要素":cell[0][15].value,"フレーム変数": cell[0][16].value,"Filled": cell[0][17].value}
        case3 = {"深層格":cell[0][18].value,"Arg":cell[0][19].value,"表層格":cell[0][20].value,"事例": cell[0][21].value,"格要素":cell[0][22].value,"フレーム変数": cell[0][23].value,"Filled": cell[0][24].value}
        case4 = {"深層格":cell[0][25].value,"Arg":cell[0][26].value,"表層格":cell[0][27].value,"事例": cell[0][28].value,"格要素":cell[0][29].value,"フレーム変数": cell[0][30].value,"Filled": cell[0][31].value}
        case5 = {"深層格":cell[0][32].value,"Arg":cell[0][33].value,"表層格":cell[0][34].value,"事例": cell[0][35].value,"格要素":cell[0][36].value,"フレーム変数": cell[0][37].value,"Filled": cell[0][38].value}
        semantic = "{}-{}-{}-{}-".format(cell[0][40].value,cell[0][41].value,cell[0][42].value,cell[0][43].value)
        value = {"verb":verb, "sentence":sentence,"semantic":semantic, "case1":case1, "case2":case2, "case3":case3, "case4":case4, "case5":case5,}
        return value


            #深層系 = semrole
            #格1 = 4~10
            #格2 = 11~17
            #格3 = 18~24
            #格4 = 25~31
            #格5 = 32~38
            #例文 = 39
    
    def chunkType(self, chunk, values, tp, fn):
        correct_chunk = {}
        if chunk.ctype == "elem":
            elem = self.elem(chunk, values, tp, fn)
            correct_chunk = elem['correct_chunk']
            tp = elem['tp']
            fn = elem['fn']
        if chunk.ctype == "adjective":
            self.adjective()
        if chunk.ctype == "verb":
            verb = self.verb(chunk, values, tp, fn)
            correct_chunk = verb['correct_chunk']
            tp = verb['tp']
            fn = verb['fn']
        return {'correct_chunk':correct_chunk, 'tp':tp, 'fn': fn}

    def returnCaseValue(self,chunk,case,tp):
            if chunk.arg[0] in case.values():
                if chunk.surface in case.values() and chunk.semrole[0] in case.values() and chunk.part in case.values():
                    value = {"Arg":None,"surface":None,"semrole":None,"part":None,"tp":tp}
                    return value
                else:
                    tp = False
                    value = {"Arg":case['Arg'],"surface":case["事例"],"semrole":case["深層格"],"part":case["表層格"],"tp":False}
                    return value

    def elem(self, chunk, values, tp, fn):
        correct_chunk = {}
        if chunk.arg:
            if chunk.arg[0] in values['case1'].values():
                correct_chunk = self.returnCaseValue(chunk,values['case1'],tp)
                tp = correct_chunk['tp']
            elif chunk.arg[0] in values['case2'].values():
                correct_chunk = self.returnCaseValue(chunk,values['case2'],tp)
                tp = correct_chunk['tp']
            elif chunk.arg[0] in values['case3'].values():
                correct_chunk = self.returnCaseValue(chunk,values['case3'],tp)
                tp = correct_chunk['tp']
            elif chunk.arg[0] in values['case4'].values():
                correct_chunk = self.returnCaseValue(chunk,values['case4'],tp)
                tp = correct_chunk['tp']
            elif chunk.arg[0] in values['case5'].values():
                correct_chunk = self.returnCaseValue(chunk,values['case5'],tp)
                tp = correct_chunk['tp']
            else:
                print("Argはあるけど正しく振られてない(fp)") #tp = FALSE retrieved = TRUE,FALSE
                tp = False
        else:
            print("Argが振られていない=(fn)")
            fn = True
        return {'correct_chunk':correct_chunk, 'tp':tp, 'fn': fn}

    def adjective(self):
        correct_chunk = {}
        tp = True
        fn = False
        return {'correct_chunk':correct_chunk, 'tp':tp, 'fn': fn}

    def verb(self, chunk, values, tp, fn):
        string_read = ""
        correct_chunk = {}
        for morph in chunk.morphs:
            string_read += morph.read
        if chunk.semantic:
            if chunk.semantic != values['semantic']:
                correct_chunk['semantic'] = values['semantic']
                tp = False
        else:
            fn = True
        if chunk.main:
            if chunk.main != values['verb']['verb_main']:
                correct_chunk['verb_main'] = values['verb']['verb_main']
                tp = False
        else:
            fn = True
        if string_read != values['verb']['verb_read']:
            correct_chunk['verb_read'] = values['verb']['verb_read']
            tp = False
        return {'correct_chunk':correct_chunk, 'tp':tp, 'fn': fn}
    
    def sumup(self, tp, fn):
        if tp:
            self.totalTp += 1
        else:
            self.totalFp += 1
        if fn:
            self.totalFn += 1
        else:
            self.totalNn += 1

    def returnTotal(self):
        return self.totalTp,self.totalFp,self.totalFn,self.totalNn
# precision適合率 = tp / (tp + fp) https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/precision.html
# recall再現率 = tp / (tp+fn) https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/recall.html
# F-value = 2*precision*recall /(precision + recall)  https://www.cse.kyoto-su.ac.jp/~g0846020/keywords/tpfptnfn.html

    def calculate_value(self):
        precision = self.totalTp / (self.totalTp + self.totalFp)
        recall = self.totalTp / (self.totalTp + self.totalFn)
        F_value = 2 * precision * recall / (precision + recall)
        return precision, recall, F_value

    def output(self,precision, recall,F_value):
        print("Precision:",precision)
        print("Recall:",recall)
        print("F_value:",F_value)

        #Precision: 0.29168911917098445
        #Recall: 0.6413013761049849
        #F_value: 0.4009915094877201

    def outputJsonfile(self,correct_json, result_json, filename,tp, fn):
        if(tp == False or fn == True):
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