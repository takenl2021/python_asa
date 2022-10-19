import numpy as np
import pymc3 as pm
import arviz as az
import matplotlib.pyplot as plt
import scipy.stats as st
import theano.tensor as tt
import theano

import json
import openpyxl

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

    for i in range(2,1000):
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
        frame_data.append(frame_id)
        v_surf_data.append(verb_index)
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

    #確率ではいらなかった
    # frame_prob = np.asarray(frame_prob).astype('float64')
    # frame_prob = frame_prob / np.sum(frame_prob)
    
    # role_prob = np.asarray(role_prob).astype('float64')
    # role_prob_tt = []
    # for each_role_prob in role_prob:
    #     each_role_prob = each_role_prob / np.sum(each_role_prob)
    #     role_prob_tt.append(each_role_prob)

    # # http://jrf.cocolog-nifty.com/statuses/2021/02/post-b7b5ba.html 確率が1でないというエラーに対する対処
    # print("frame_prob", frame_prob)
    # print("role_prob", role_prob_tt)
    F = len(mapping_json['sem_mapping']) #概念フレーム数
    V = len(mapping_json['verb_mapping']) #意味役割数

    n_sample = 998
    with pm.Model() as model:

        # ベースデータ
        fdata = pm.Data("fdata",frame_data) #dataって何だろう #data = [fid]
        vdata = pm.Data("vdata",v_surf_data) #dataって何だろう #data = [v_surf]

        
        # 混合比率
        pi_fid = pm.Dirichlet("pi_fid", a=np.ones(F), shape=F)
        pi_v_surf = pm.Dirichlet("pi_v_surf", a=np.ones(V), shape=V)
        
        # クラスタごとの正規分布の平均(shapeに合わせてブロードキャストされる)
        mu_fid = pm.Normal("mu_fid", mu=0, sigma=10, shape=F)
        mu_v_surf = pm.Normal("mu_v_surf", mu=0, sigma=10, shape=V)
        
        # クラスタごとの正規分布の標準偏差(shapeに合わせてブロードキャストされる)
        sigma_fid = pm.HalfCauchy("sigma_fid", beta=3, shape=F)
        sigma_v_surf = pm.HalfCauchy("sigma_v_surf", beta=3, shape=V)

        # クラスタ割り当てを示す潜在変数
        z_fid = pm.Categorical("z_fid", p=pi_fid, shape=n_sample)
        z_v_surf = pm.Categorical("z_v_surf", p=pi_v_surf, shape=n_sample)

        # 観測モデル
        x_fid = pm.Normal("x_fid", mu=mu_fid[z_fid], sigma=sigma_fid[z_fid], observed=fdata)
        x_v_surf = pm.Normal("x_v_surf", mu=mu_v_surf[z_v_surf], sigma=sigma_v_surf[z_v_surf], observed=vdata)

    with model:
        trace = pm.sample(5000, tune=1000, chains=1, random_seed=1, return_inferencedata=True)

    print("trace mu==",trace.posterior)

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

        