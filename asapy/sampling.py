from pgmpy.factors.discrete import TabularCPD
from pgmpy.models import BayesianModel
from pgmpy.sampling import GibbsSampling

# ベイジアンネットワークの構造
model = BayesianModel([
    # ('親ノード', '子ノード')
    ('battery', 'gauge'),
    ('fuel', 'gauge'),
])

battery_cpd = TabularCPD(
    variable='battery',
    variable_card=2,
    # values[0]: empty, values[1]: full
    values=[[.1], [.9]])

fuel_cpd = TabularCPD(
    variable='fuel',
    variable_card=2,
    values=[[.1], [.9]])

gauge_cpd = TabularCPD(
    variable='gauge',
    variable_card=2,
    values = [[.9, .8, .8, .2],
             [.1, .2, .2, .8]],
    evidence = ['battery', 'fuel'],
    evidence_card=[2, 2]
)

model.add_cpds(battery_cpd, fuel_cpd, gauge_cpd)

gibbs = GibbsSampling(model)
gen = gibbs.generate_sample(size=1)
print(gen)