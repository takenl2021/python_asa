import numpy as np
import pymc3 as pm
import arviz as az
import matplotlib.pyplot as plt
import scipy.stats as st
import theano.tensor as tt
import theano

import json
import openpyxl
import time

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

if __name__ == '__main__':
    #DATA_NUM = 24130 #旧データ
    DATA_NUM = 24577

    #mappingのjsonを読み込む
    #キーは〇〇_mapping
    json_open = open('mapping.json', 'r')
    mapping_json = json.load(json_open)

    #Excelからデータ読み込み
    #旧データ
    #wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/pth20210305.xlsx') #should be changed
    #sheet1 = wb['pth20210305-sjis']

    wb = openpyxl.load_workbook('/home/ooka/study/python_asa/asapy/data/動詞辞書_220711.xlsx') #should be changed
    sheet1 = wb['dup_checked_pth']

    #学習データ
    #まずそれぞれのマッピングサイズ分1で埋めてカウントアップしていく
    #その後長さで割って確率化

    frame_data = []
    v_surf_data = []

    for i in range(2,48):
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
        sem_index = mapping_json['sem_mapping'].get(semantic)
        verb_index = mapping_json['verb_mapping'].get(values['verb']['verb_main'])
        if frame_id != None:
            frame_data.append(frame_id)
        else:
            frame_data.append(1)
        if verb_index != None:
            v_surf_data.append(verb_index)
        else:
            v_surf_data.append(1)
        if values['sentence'] == None:
                continue
        else:
            if values["case1"]["arg"] != "false" and values["case1"]["arg"] != None and values["case1"]["arg"] != False:
                role_index = mapping_json['role_mapping'].get(values["case1"]["role"])

            if values["case2"]["arg"] != "false" and values["case2"]["arg"] != None and values["case2"]["arg"] != False:
                role_index = mapping_json['role_mapping'].get(values["case2"]["role"])

            if values["case3"]["arg"] != "false" and values["case3"]["arg"] != None and values["case3"]["arg"] != False:
                role_index = mapping_json['role_mapping'].get(values["case3"]["role"])

            if values["case4"]["arg"] != "false" and values["case4"]["arg"] != None and values["case4"]["arg"] != False:
                role_index = mapping_json['role_mapping'].get(values["case4"]["role"])

            if values["case5"]["arg"] != "false" and values["case5"]["arg"] != None and values["case5"]["arg"] != False:
                role_index = mapping_json['role_mapping'].get(values["case5"]["role"])

    F = len(mapping_json['sem_mapping']) #概念フレーム数
    print(F)
    print(frame_data)
    V = len(mapping_json['verb_mapping']) #意味役割数
    print("V=",V)
    print(v_surf_data)

    start = time.time()
    n_sample = 48 #ValueError: Input dimension mis-match. (input[0].shape[0] = 28, input[1].shape[0] = 998) <=?エラー

    with pm.Model() as model:

        # ベースデータ
        fiddata = pm.Data("fiddata",frame_data) #dataって何だろう #data = [fid]
        vdata = pm.Data("vdata",v_surf_data)
        
        # 混合比率
        pi_fid = pm.Dirichlet("pi_fid", a=np.ones(F))
        pi_v_surf = pm.Dirichlet("pi_v_surf", a=np.ones(V))

        # クラスタ割り当てを示す潜在変数
        z_fid = pm.Categorical("z_fid", p=pi_fid, shape=n_sample)
        x_fid = pm.Categorical("x_fid",p=pi_v_surf[z_fid],shape=n_sample)
        # 観測モデル

    with model:
        trace = pm.sample(500, tune=1000, chains=1, random_seed=1, return_inferencedata=True, init='adapt_diag')
    print("trace mu==",trace.posterior)
    z_samples = trace.posterior['z_fid'][0].values
    print("z_sample_shape",z_samples.shape)
    print(az.summary(trace))
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    az.plot_posterior(trace,point_estimate="mode")
    exit()



#各文書に対する概念フレームラベル列
    doc_frame_labels = np.random.choice(F, size=doc_size, p=frame_prob)
# print(doc_frame_labels) # [0 1 0 0 0 0 0 0 0 1 0 1 0 2 0 ...] #概念フレームラベル列

# 各文書のframeに対して6個 意味役割がでたとする
    docs_roles = []
    for frame in doc_frame_labels:
        local_roles = np.random.choice(R, size=6, p=role_prob_tt[frame]) #フレームごとの分布
        print("local=",local_roles, " frame=",frame)
        docs_roles.append(local_roles) # [意味役割ラベル列]のリスト
    #check_role_dist[frame].extend(local_roles) # 確認用配列

    docs_roles_np = np.array(docs_roles) #numpy化  docs(100) x role_instance(6)
# print("docs_roles=",docs_roles_np) #各フレームに対する意味役割 #本当は意味役割ラベルは均等列ではない

#生成データの分布の確認
#import collections
#for frame in range(0,3):
#    c = collections.Counter(check_role_dist[frame])
#    print(f'frame={frame},  role={c[0]}, {c[1]}, {c[2]}, {c[3]}, {c[4]} ')


###################### データ ###############################################
# 上記データを全てflattenにしたデータに変える 
# これが本当にシステムに入れるデータ形式
# 1) まず dataそのもの
    data_flatten = np.reshape(docs_roles_np, docs_roles_np.shape[0]*docs_roles_np.shape[1])
    print("data_flatten=",len(data_flatten))

# 2) 各文書に対するframeIDを1個1個の意味役割に貼り付ける
    frame_index = np.repeat(doc_frame_labels, docs_roles_np.shape[1])
    print("frame_index=",len(frame_index))
# 以上で各意味役割のラベルと各意味役割に対するframeを割り当てた列を作成した

#############################################################################

    n_sample = 500 #1000
    K = len(mapping_json['role_mapping'])
    #学習段階のモデル

    with pm.Model() as model:

        # ベースデータ
        bdata = pm.Data("bdata",data) #dataって何だろう #data = [fid]
        bdata = pm.Data("bdata",data) #dataって何だろう #data = [v_surf]

        
        # 混合比率
        pi = pm.Dirichlet("pi", a=np.ones(K), shape=K)
        
        # クラスタごとの正規分布の平均(shapeに合わせてブロードキャストされる)
        mu = pm.Normal("mu", mu=0, sigma=10, shape=K)
        
        # クラスタごとの正規分布の標準偏差(shapeに合わせてブロードキャストされる)
        sigma = pm.HalfCauchy("sigma", beta=3, shape=K)

        # クラスタ割り当てを示す潜在変数
        z = pm.Categorical("z", p=pi, shape=n_sample)

        # 観測モデル
        x = pm.Normal("x", mu=mu[z], sigma=sigma[z], observed=bdata)

    #TODO
    for frame_number in renge(0,F):
        for role_data in role_prob_tt:
            local_roles = np.random.choice(R, size=6, p=role_data[frame_number])
            print("local=",local_roles, " frame=",frame)
            docs_roles.append(local_roles)

        