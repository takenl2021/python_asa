# ライブラリー読み込み
import numpy as np
import pymc3 as pm
import arviz as az
import matplotlib.pyplot as plt
import scipy.stats as st
import theano.tensor as tt
import theano

# 岩田 トピックモデル p.34 混合ユニグラム
#   theta_frame 〜 Dir (a) #概念フレームの生成確率 (3個の概念フレームとすると[0.5, 0.3, 0.2] のようなもの)
#   theta_frame = {0,1,2}  # 例えば {0:状態変化，1:活動，2:状態}
#   phi_k  〜 Dir(b) # ある概念フレームでの意味役割の分布. 概念kごとに違う分布になる
#                    　例) 意味役割5種類とすると [0.1, 0.2, 0.1, 0.3, 0.3] のような分布を出す
#                      role = {0:動作主，1:対象，2:相手，3:時間，4:場所}
#   phi_k  = {0,1,2,3,4}   frame=0, frame=1, frame=2のそれぞれで確率分布が違う
#
#   z_d  〜 Categorial (theta_frame)  #ある文 d に対する概念フレーム
#     ある文 d=0 の概念フレームz_d = {0,1,2}のどれか

#   各文の意味役割 について{n:1〜 N_d}番目の項に対して
#   r_dn 〜 Categorial (phi_z_d)
#     文書d=1 の n=3番目の意味役割は 対象なら r_13 = 1  となる．
#     この時の概念フレームが状態変化ならば phi_z_1 = 0 となる


# グラフの表示設定
#plt.style.use('ggplot') #グラフスタイル
#plt.rcParams['figure.figsize'] = [12, 9] # グラフサイズ

# データ1
# 文書0  z_0 = 状態変化  r_0 = 動作主，対象，相手, 時間，場所  # 5つの項
# 文書1  z_1 = 活動      r_1 = 動作主，時間，場所              # 3つの項
# 文書2  z_2 = 状態      r_2 = 対象，場所，対象                # 3つの項
# 文書3  z_3 = 状態変化  r_3 = 動作主，対象，時間，場所        # 4つの項

# テストデータ  項は3つとする
# 文書0  z_0 と r_0 = ?, ?, ?

num_dice1 = np.array([2]) #1回だけサイコロを振って '3'がでた．(1から6までが 0から5に対応)

F = 3  # 概念フレーム数 (岩田の本のトピック数K)
R = 5  # 意味役割種類数 (岩田の本の単語数V)

# ------- 学習データの作成 --------
# ここは本来不要 データ読むだけ
# ただし，作成したモデルが正しいかどうか検証するために作る必要がある
# 真のframeの分布を作る
frame_prob = np.array([0.5,0.2,0.3]) # 状態変化 0.5,  活動 0.3,  状態 0.2
role_prob = np.array([[0.3, 0.3, 0.1, 0.2, 0.1],  #状態変化の意味役割分布 (動作主，対象, 相手, 時間, 場所)
                     [0.5, 0.2, 0.1, 0.1, 0.1],  # 活動
                     [0.01, 0.7, 0.01, 0.15, 0.13]])  # 状態
np.random.seed(1)

doc_size = 10000  # 文書100

#各文書に対する概念フレームラベル列
doc_frame_labels = np.random.choice(F, size=doc_size, p=frame_prob)
# print(doc_frame_labels) # [0 1 0 0 0 0 0 0 0 1 0 1 0 2 0 ...] #概念フレームラベル列

# 各文書のframeに対して6個 意味役割がでたとする
docs_roles = []
check_role_dist = {}
check_role_dist[0] = []
check_role_dist[1] = []
check_role_dist[2] = []
for frame in doc_frame_labels:
    local_roles = np.random.choice(R, size=6, p=role_prob[frame]) #フレームごとの分布
    print("local=",local_roles, " frame=",frame)
    docs_roles.append(local_roles) # [意味役割ラベル列]のリスト
    check_role_dist[frame].extend(local_roles) # 確認用配列

docs_roles_np = np.array(docs_roles) #numpy化  docs(100) x role_instance(6)
# print("docs_roles=",docs_roles_np) #各フレームに対する意味役割 #本当は意味役割ラベルは均等列ではない

#生成データの分布の確認
import collections
for frame in range(0,3):
    c = collections.Counter(check_role_dist[frame])
    print(f'frame={frame},  role={c[0]}, {c[1]}, {c[2]}, {c[3]}, {c[4]} ')


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


# 3) 単語の分布も正解があるのだから学習させる
# 各トピックの分布用のデータを与える
voc0 = []
voc1 = []
voc2 = []
for frame, role_label in zip (doc_frame_labels, docs_roles_np):
    if frame == 0:
        voc0.append(role_label)
    elif frame == 1:
        voc1.append(role_label)
    elif frame == 2:
        voc2.append(role_label)
    else:
        print("error")
        exit(0)
voc0 = np.array(voc0)
voc1 = np.array(voc1)
voc2 = np.array(voc2)
voc0_flatten = np.reshape(voc0, voc0.shape[0]*voc0.shape[1])
voc1_flatten = np.reshape(voc1, voc1.shape[0]*voc1.shape[1])
voc2_flatten = np.reshape(voc2, voc2.shape[0]*voc2.shape[1])
print("voc=",voc2)
print("voc=",voc2_flatten)


#############################################################################





with pm.Model() as model:
    
    # 事前分布 Dir
    theta = pm.Dirichlet("theta", a=np.ones(F)) # shape不要 Fと同じ
    #phi = pm.Dirichlet("phi", a=np.ones(R),shape=(F,R)) #合ってる．topic x Vocabulary

    #フレームごとの意味役割の分布
    phi0 = pm.Dirichlet("phi0",a=np.ones(R)) # np.array([0.2, 0.5, 0.1, 0.1, 0.1]))
    phi1 = pm.Dirichlet("phi1",a=np.ones(R)) # np.array([0.5, 0.2, 0.1, 0.1, 0.1]))
    phi2 = pm.Dirichlet("phi2",a=np.ones(R))

    z_phi0 = pm.Categorical('z_phi0', p=phi0, observed=voc0_flatten)
    z_phi1 = pm.Categorical('z_phi1', p=phi1, observed=voc1_flatten)
    z_phi2 = pm.Categorical('z_phi2', p=phi2, observed=voc2_flatten)

    wphi = tt.stack(phi0,phi1,phi2)
    #print("wphi=",wphi.ndim)
    #print("wphi[0]=",wphi[0])
    #print("wphi[1]=",wphi[1])
    #print("wphi[2]=",wphi[2])
    # print("pp=",theano.pp(wphi))
    # NUTS: [phi2, phi1, phi0, phi, theta]
    # 最終的にアルファベット + 数字が多い順に並ぶみたい
    
    # 文に対するフレームの割り当て
    z_d = pm.Categorical('z_d', p=theta, observed=doc_frame_labels) #概念フレーム教える
    #  # z_d = pm.Categorical('z_d', p=theta, shape=doc_size) #概念フレーム教えない => ダメ

    # 観測モデル
    # print("docs_roles_np=",docs_roles_np.shape)
    p = wphi[doc_frame_labels][frame_index]
    #print("p =",p.ndim)
    #print("typep",type(p))

    role = pm.Categorical('role', p=p, observed=data_flatten)

    
    # 事後分布からデータ生成
    trace = pm.sample(return_inferencedata=True)
    print ("trace",trace)
    #print("posterior",trace.posterior.theta.values)
    
    #サマリーの表示
    print(az.summary(trace)) # defaultは信頼区間が 0.97ででる

    #for k, v in trace.items():
    #    print("k=",k, " v=", v)

    #保存
    #import pickle
    #with open('trace_file.pickle','wb') as f:
    #   pickle.dump(trace,f)

    '''
    p0 = np.percentile(trace.get_values('phi0',chanins=[0]),50,axis=0)
    p1 = np.percentile(trace.get_values('phi0',chanins=[1]),50,axis=0)
    pp = pd.DataFrame( {'p00':phi0[:,0],
                        'p01':p0[:,1],
                        'p02':p0[:,2],
                        'p10':p1[:,0],
                        'p11':p1[:,1],
                        'p12':z1[:,2],})
    print(pp.corr())
    '''
    exit(0)

    
    #予測分布
    # データがあるときは検証用データを推論したモデルに入力
    # pm.set_data({"x": x_new})

    # 予測分布からサンプリング
    # dataで与えたのと同じ長さのものを 1000回出す

    pred = pm.sample_posterior_predictive(trace, samples=1000, random_seed=1) 
print("pred==",pred) # type は np.array
predicted = np.ravel(pred['role']) #平坦化する
#各さいの目の頻度を数え上げて確率を求める
print("z_d shape=",pred['z_d'].shape)
print("role shape=",predicted.shape)
import collections
c = collections.Counter(predicted)
print(c)
total = 0.0
for sainome in range(0,6):
    total += c[sainome]
for sainome in range(0,6):
    print(sainome, " = ",c[sainome]/total)


    #az.plot_posterior(trace, point_estimate='mode')
    #plt.show()