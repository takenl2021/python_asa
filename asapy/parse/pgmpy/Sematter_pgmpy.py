from asapy.result.Result import Result
from asapy.result.Morph import Morph
from asapy.result.Chunk import Chunk
from asapy.parse.pgmpy.Calculate_pgmpy import Calculate
from asapy.parse.pgmpy.Adjunct_pgmpy import Adjunct
from asapy.parse.pgmpy.NounStructure_pgmpy import NounStructure

import pickle
import os
import openpyxl

from pgmpy.inference import VariableElimination

# 語義，意味役割を付与するためのクラス


class Sematter():

    def __init__(self, frames: dict, categorys: dict, nouns: dict) -> None:
        self.frames = frames
        self.nouns = nouns
        self.calc = Calculate(frames)
        self.adjunct = Adjunct()
        self.nounstruct = NounStructure(nouns, frames)
        self.ve_role = self.__getVe_role('../utils/model_pth_role.pickle')
        self.ve_arg = self.__getVe_role('../utils/model_pth_arg.pickle')
        # self.sheet = self.__getSheet("filepath")
        # self.model_role = self.__getModel('../utils/model_pth_role.pickle')
        # self.model_arg = self.__getModel('../utils/model_pth_arg.pickle')
        # self.cpd_surface = self.model_role.get_cpds('surface')
        # self.cpd_pos = self.model_role.get_cpds('pos')
        # self.cpd_rel = self.model_role.get_cpds('rel')
        # self.cpd_sem = self.model_role.get_cpds('sem')
        # self.cpd_role = self.model_role.get_cpds('role')
        # self.cpd_verb = self.model_role.get_cpds('verb')
        # self.cpd_voice = self.model_role.get_cpds('voice')
        # self.cpd_arg = self.model_arg.get_cpds('arg')
        # self.cpd_arg_surface = self.model_arg.get_cpds('surface')
        # self.cpd_arg_pos = self.model_arg.get_cpds('pos')
        # self.cpd_arg_rel = self.model_arg.get_cpds('rel')
        # self.cpd_arg_sem = self.model_arg.get_cpds('sem')
        # self.cpd_arg_verb = self.model_arg.get_cpds('verb')
        # self.cpd_voice = self.model_arg.get_cpds('voice')

    def __getModel(self , filepath):
        #jsonバージョンは model_json.pickle
        with open(filepath, mode='rb') as f:
            model = pickle.load(f) 
        return model
    
    def __getVe_role(self, filepath):
        model = self.__getModel(filepath)
        ve = VariableElimination(model)
        return ve
    
    def __getVe_arg(self, filepath):
        model = self.__getModel(filepth)
        ve = VariableElimination(model)
        return ve

    def __getSheet(self, filepath:str):
        wb = openpyxl.load_workbook('data/pth20210305.xlsx')
        sheet = wb['pth20210305-sjis']
        return sheet

    def __getSemantics(self,verb):
        semantics = []
        lastrow = self.sheet.max_row
        myRenges = self.sheet['C2:C' + str(lastrow)]
        for rows in myRenges:
            semantic = ""
            for cell in rows:
                if cell.value != None:
                    if verb in cell.value:
                        obj = "AO{}:AS{}".format(cell.row,cell.row)
                        cells = self.sheet[obj]
                        for row in cells:
                            for frame in row:
                                if frame.value == None:
                                    semantic += "-"
                                else:
                                    semantic += "{}-".format(frame.value)
                        if semantic != "-----":
                            semantics.append(semantic)
        return semantics

    def __esti_role_sem(self , verbchunk, linkchunks, semantics):
        semantic_indexs = []
        for linkchunk in linkchunks:
            indexs = None
            cpd = -1000
            if linkchunk.morphs[0].pos in self.cpd_pos.state_names['pos']:
                pos_index = self.cpd_pos.state_names['pos'].index(linkchunk.morphs[0].pos)
            else:
                pos_index = None
            if linkchunk.main in self.cpd_surface.state_names['surface']:
                surface_index = self.cpd_surface.state_names['surface'].index(linkchunk.main)
            else:
                surface_index = None
            if linkchunk.part in self.cpd_rel.state_names['rel']:
                rel_index = self.cpd_rel.state_names['rel'].index(linkchunk.part)
            else:
                rel_index = None
            if verbchunk.main in self.cpd_rel.state_names['verb']:
                verb_index = self.cpd_rel.state_names['verb'].index(verbchunk.main)
            else:
                verb_index = None
            if verbchunk.voice in self.cpd_rel.state_names['voice']:
                voice_index = self.cpd_rel.state_names['voice'].index(verbchunk.voice)
            else:
                voice_index = None
            for semantic in semantics:
                semantic_indexs.append(self.cpd_sem.state_names['sem'].index(semantic))

            for i in range(len(self.cpd_role.values)):
                for semantic_index in semantic_indexs:
                    cpd_new = self.cpd_role.values[i][semantic_index] * (self.cpd_pos.values[pos_index][i] if pos_index != None else 1) * (self.cpd_surface.values[surface_index][i] if surface_index != None else 1)* (self.cpd_rel.values[rel_index][i] if rel_index != None else 1) * (self.cpd_verb.values[verb_index][i] if verb_index != None else 1) * (self.cpd_voice.values[voice_index][i] if voice_index != None else 1)
                    if cpd_new > cpd:
                        cpd = cpd_new
                        indexs = {"sem": semantic_index, "role": i}
            cpd = -1000
            for i in range(len(self.cpd_arg.values)):
                for semantic_index in semantic_indexs:
                    cpd_new = self.cpd_arg.values[i][semantic_index] * (self.cpd_arg_pos.values[pos_index][i] if pos_index != None else 1) * (self.cpd_arg_surface.values[surface_index][i] if surface_index != None else 1)* (self.cpd_arg_rel.values[rel_index][i] if rel_index != None else 1) * (self.cpd_arg_verb.values[verb_index][i] if verb_index != None else 1) * (self.cpd_voice.values[voice_index][i] if voice_index != None else 1)
                    if cpd_new > cpd:
                        cpd = cpd_new
                        indexs['arg'] = i
            self.__setAll(indexs, linkchunk, verbchunk)
        
    def __setAll(self, indexs, linkchunk, verbchunk):
        if indexs == None:
            return 
        linkchunk.semrole.append(self.cpd_role.state_names['role'][indexs["role"]])
        verbchunk.semantic = self.cpd_role.state_names['sem'][indexs["sem"]]
        linkchunk.arg.append(self.cpd_arg.state_names['arg'][indexs["arg"]])


    def parse(self, result: Result) -> None:
        verbchunks = self.__getSemChunks(result)
        for verbchunk in verbchunks:
            #semantics = self.__getSemantics(verbchunk.main)
            linkchunks = self.__getLinkChunks(verbchunk)
            self.__setAnotherPart(linkchunks)
            #self.__esti_role_sem(verbchunk, linkchunks, semantics) #CPDの計算
            self.calc_model(verbchunk,verbchunk.main,linkchunks, result) #VariableElimination
            #frame = self.calc.getFrame(verbchunk.main, linkchunks)
            # if frame:
            #     semantic, similar, insts = frame
            #     self.__setSemantic(semantic, similar, verbchunk)
            #     self.__setSemRole(insts)
            #     self.__setArg(insts)
            #     self.__setSpecialSemantic(verbchunk)
            #     self.adjunct.parse(verbchunk.modifiedchunks)
        # nounchunks = self.__getNounChunks(result)
        # for nounchunk in nounchunks:
        #     self.nounstruct.parse(nounchunk)
        # self.__setInversedSemantic(result)
        return result

    def calc_model(self, verbchunk, verb, linkchunks, result): #予測
        for linkchunk in linkchunks:
            try:
                estimate_role = self.ve_role.map_query(variables=['sem','role'], evidence={'verb':verb,'surface': linkchunk.main, 'pos':linkchunk.morphs[0].pos,'rel':linkchunk.part,'voice':verbchunk.voice})
                estimate_arg = self.ve_arg.map_query(variables=['sem','arg'], evidence={'verb':verb,'surface': linkchunk.main, 'pos':linkchunk.morphs[0].pos,'rel':linkchunk.part,'voice':verbchunk.voice})
                self.__setRole_estimate(linkchunk, verbchunk , estimate_role)
                self.__setArg_estimate(linkchunk, estimate_arg)
                #self.adjunct.parse(verbchunk.modifiedchunks)
            except:
                print("ERROR occured")
                #self.adjunct.parse(verbchunk.modifiedchunks)
                # frame = self.calc.getFrame(verbchunk.main, linkchunks)
                # if frame:
                #     semantic, similar, insts = frame
                #     self.__setSemantic(semantic, similar, verbchunk)
                #     self.__setSemRole(insts)
                #     self.__setArg(insts)
                #     self.__setSpecialSemantic(verbchunk)
                #     self.adjunct.parse(verbchunk.modifiedchunks)

            #TODO try-exceptの処理の改善->精度の向上

    def __setRole_estimate(self, linkchunk, verbchunk, esti):
        if esti['role']:
            linkchunk.semrole.append(esti['role'])
        if esti['sem']:
                verbchunk.semantic = esti['sem']
    
    def __setArg_estimate(self, linkchunk, esti):
        if esti['arg']:
            linkchunk.arg.append(esti['arg'])
    #
    # 係り先である節を取得
    #
    def __getSemChunks(self, result: Result) -> list:
        # chunks = [c for c in result.chunks if c.ctype != 'elem' and self.frames.isFrame(c.main)]
        chunks = [c for c in result.chunks if c.ctype != 'elem']
        return chunks

    #
    # 係り先の節を渡して，その係り元を取得
    #
    def __getLinkChunks(self, verbchunk: Chunk) -> list:
        if verbchunk.modifyingchunk and (verbchunk.modifyingchunk.ctype == 'elem'):
            can = [c.part for c in verbchunk.modifiedchunks]
            verbchunk.modifyingchunk.another_parts = {'が', 'を', 'に'} - set(can)
            verbchunk.modifiedchunks.append(verbchunk.modifyingchunk)
        return verbchunk.modifiedchunks

    #
    # 助詞の言い換え候補があるものに対して，言い換えの助詞を付与
    #
    def __setAnotherPart(self, chunks: list) -> None:
        for chunk in chunks:
            for morph in chunk.morphs:
                if '格助詞' in morph.pos and chunk.part in {'に', 'へ'}:
                    chunk.another_parts = list({'に', 'へ'} - set(chunk.part))
                elif '係助詞' in morph.pos:
                    chunk.another_parts = ['が', 'を']
                else:
                    pass

    #
    # 曖昧性を解消したフレームのデータより語義を付与
    # @param semantic Calculateクラスより取得したデータ
    # @param verbchunk 語義を付与する文節
    #
    def __setSemantic(self, semantic: str, similar: float, verbchunk: Chunk) -> None:
        verbchunk.semantic = semantic
        verbchunk.similar = similar

    #
    # 曖昧性を解消したフレームのデータより意味役割を付与
    # @param semantic Calculateクラスより取得したデータ
    #
    def __setSemRole(self, insts: list) -> None:
        for instset in insts:
            similar, icase, chunk = instset
            chunk.semrole.append(icase['semrole'])
            chunk.similar = similar
            if icase['category'] in chunk.category:
                chunk.category.append(icase['category'])
                chunk.category = list(set(chunk.category))

    def __setArg(self, insts: list) -> None:
        for instset in insts:
            similar, icase, chunk = instset
            if icase['arg']: chunk.arg.append(icase['arg'])
            chunk.similar = similar
            if icase['category'] in chunk.category:
                chunk.category.append(icase['category'])
                chunk.category = list(set(chunk.category))

    def __setSpecialSemantic(self, chunk: Chunk) -> None:
        semantics = (chunk.semantic.split('-') + ['' for i in range(5)])[:5]
        if semantics[1] == '位置変化' and semantics[3] == '着点への移動':
            if any([True if '対象' in c.semrole else False  for c in chunk.modifiedchunks]):
                pass
            else:
                for c in chunk.modifiedchunks:
                    if c.part == 'が':
                        c.semrole.append('対象')
        elif semantics[1] == '位置変化' and semantics[2] == '位置変化（物理）（人物間）' and semantics[3] == '他者からの所有物の移動':
            if any([True if '着点' in c.semrole else False  for c in chunk.modifiedchunks]):
                pass
            else:
                for c in chunk.modifiedchunks:
                    if '動作主' in c.semrole or '経験者' in c.semrole:
                        c.semrole.append('着点')

    def __getNounChunks(self, result: Result) -> list:
        chunks = [chunk for chunk in result.chunks if self.nouns.isFrame(chunk.main)]
        return chunks

    def __setInversedSemantic(self, result: Result) -> None:
        for chunk in result.chunks:
            self.__getModChunk(chunk)

    def __getModChunk(self, chunk: Chunk) -> None:
        if chunk.modifyingchunk:
            chunk.modifiedchunks.append(chunk.modifyingchunk)
