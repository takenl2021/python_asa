import time
from asapy.result.Result import Result
from evaluate.Evaluate import Evaluate

EXAMPLES = 24577 #should be changed

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
