import pickle

with open("model_pth_arg.pickle", mode='rb') as f:
        model = pickle.load(f) 

a = model.get_cpds('sem')
print(a.state_names['arg'])