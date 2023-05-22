
# ASAで使用する辞書を指定するクラス


class JsonFile():

    def __init__(self):
        self.frame = "dict/excel2json.json" #新データ excel2json 旧データ frames.json or new_frames2.json
        self.dicframe = "dict/new_argframes.dic"
        self.cchart = "dict/ccharts.json"
        self.diccchart = "dict/ccharts.dic"
        self.verb = "dict/verbs.json"
        self.category = "dict/new_categorys.json"
        self.idiom = "dict/idioms.json"
        self.filter = "dict/filters.json"
        self.dicfilter = "dict/filters.dic"
        self.compoundPredicate = "dict/compoundPredicates.json"
        self.noun = "dict/NounTest.json"
