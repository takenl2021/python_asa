import CaboCha
from result.Result import Result
from result.Chunk import Chunk
from result.Morph import Morph


class Analyzer():

    def __init__(self, analyzertype, code):
        if analyzertype == 'cabocha':
            self.analyzer = CaboCha.Parser("-f1 -n1")

    def parse(self, line):
        m_id = 0
        result = Result(line)
        tree = self.analyzer.parse(line)
        line_list = tree.toString(CaboCha.FORMAT_LATTICE).split("\n")
        for line in line_list:
            if line == "EOS":
                break
            if line.startswith("* "):
                result.addChunk(Chunk(line))
                m_id = 0
            elif line != "EOS":
                result.chunks[-1].addMorph(Morph(m_id, line))
                m_id += 1
        return result