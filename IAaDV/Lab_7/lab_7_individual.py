import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

MIN_INCOME = 0
MAX_INCOME = 50000

MIN_DEBT = 0
MAX_DEBT = 100000

MIN_LIMIT = 0
MAX_LIMIT = 200000

income = ctrl.Antecedent(np.arange(MIN_INCOME, MAX_INCOME + 1, 500), 'income')
debt = ctrl.Antecedent(np.arange(MIN_DEBT, MAX_DEBT + 1, 1000), 'debt')
limit = ctrl.Consequent(np.arange(MIN_LIMIT, MAX_LIMIT + 1, 1000), 'limit')


income['low'] = fuzz.gaussmf(income.universe, 0, 8000)
income['medium'] = fuzz.gaussmf(income.universe, 20000, 6000)
income['high'] = fuzz.gaussmf(income.universe, 50000, 10000)

debt['low'] = fuzz.trapmf(debt.universe, [0, 0, 5000, 15000])
debt['manageable'] = fuzz.trapmf(debt.universe, [10000, 20000, 40000, 50000])
debt['critical'] = fuzz.trapmf(debt.universe, [40000, 60000, MAX_DEBT, MAX_DEBT])

limit['denied'] = fuzz.trimf(limit.universe, [0, 0, 10000])
limit['small'] = fuzz.trimf(limit.universe, [5000, 20000, 50000])
limit['standard'] = fuzz.trimf(limit.universe, [40000, 80000, 120000])
limit['vip'] = fuzz.trapmf(limit.universe, [100000, 150000, MAX_LIMIT, MAX_LIMIT])

income.view()
debt.view()
limit.view()

rule1 = ctrl.Rule(debt['critical'], limit['denied'])
rule2 = ctrl.Rule(income['low'] & debt['low'], limit['small'])
rule3 = ctrl.Rule(income['low'] & debt['manageable'], limit['denied'])
rule4 = ctrl.Rule(income['medium'] & debt['low'], limit['standard'])
rule5 = ctrl.Rule(income['high'] & debt['low'], limit['vip'])
rule6 = ctrl.Rule(income['high'] & debt['manageable'], limit['standard'])

scoring_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
scoring = ctrl.ControlSystemSimulation(scoring_ctrl)

income_val = float(input(f"Enter income ({MIN_INCOME}-{MAX_INCOME}): "))
if income_val < MIN_INCOME or income_val > MAX_INCOME:
    raise ValueError(f"Income must be between {MIN_INCOME} and {MAX_INCOME}.")
scoring.input['income'] = income_val

debt_val = float(input(f"Enter debt ({MIN_DEBT}-{MAX_DEBT}): "))
if debt_val < MIN_DEBT or debt_val > MAX_DEBT:
    raise ValueError(f"Debt must be between {MIN_DEBT} and {MAX_DEBT}.")
scoring.input['debt'] = debt_val

scoring.compute()

print(f"Recommended Credit Limit: {scoring.output['limit']:.2f} UAH")

limit.view(sim=scoring)

plt.show()