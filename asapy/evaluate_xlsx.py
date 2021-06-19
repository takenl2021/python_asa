import time
from asapy.ASA import ASA
from asapy.result.Result import Result
from evaluate.Evaluate import Evaluate

EXAMPLES = 24130 #should be changed

if __name__ == '__main__':
    init_start = time.time()
    evaluate = Evaluate()
    init_time = time.time() - init_start
    print("起動時間:{0}".format(init_time) + "[sec]")
    start = time.time()    
    evaluate.calculate()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    print('終了')



#TODO 評価の仕方を考える　竹内先生に助けを求める。
#TODO diffの整理整頓 nullの時に出さない
#TODO 

#参考になりそうなやつ 雲隠れ