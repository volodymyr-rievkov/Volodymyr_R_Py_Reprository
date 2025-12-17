import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

MIN_TIP = 0
MAX_TIP = 25

MIN_GRADE = 0
MAX_GRADE = 10

food = ctrl.Antecedent(np.arange(MIN_GRADE, MAX_GRADE, 1), 'food')
service = ctrl.Antecedent(np.arange(MIN_GRADE, MAX_GRADE, 1), 'service')
tip = ctrl.Consequent(np.arange(MIN_TIP, MAX_TIP, 1), 'tip')

food.automf(3)
service.automf(3)

tip['low'] = fuzz.trimf(tip.universe, [MIN_TIP, MIN_TIP, MAX_TIP / 2])
tip['medium'] = fuzz.trimf(tip.universe, [MIN_TIP, MAX_TIP / 2, MAX_TIP])
tip['high'] = fuzz.trimf(tip.universe, [MAX_TIP / 2, MAX_TIP, MAX_TIP])

food.view()
service.view()
tip.view()

rule1 = ctrl.Rule(service['poor'] | food['poor'], tip['low'])
rule2 = ctrl.Rule(service['average'], tip['medium'])
rule3 = ctrl.Rule(service['average'] & food['good'], tip['high'])
rule4 = ctrl.Rule(service['good'] & food['good'], tip['high'])

tipping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
tipping = ctrl.ControlSystemSimulation(tipping_ctrl)

food_grade = float(input(f"Enter food grade ({MIN_GRADE}-{MAX_GRADE}): "))
if food_grade < MIN_GRADE or food_grade > MAX_GRADE:
    raise ValueError(f"Food grade must be between {MIN_GRADE} and {MAX_GRADE}.")
tipping.input['food'] = food_grade

service_grade = float(input(f"Enter service grade ({MIN_GRADE}-{MAX_GRADE}): "))
if service_grade < MIN_GRADE or service_grade > MAX_GRADE:
    raise ValueError(f"Service grade must be between {MIN_GRADE} and {MAX_GRADE}.")
tipping.input['service'] = service_grade

tipping.compute()

print(f"Recommended tip: {tipping.output['tip']:.2f}%")

tip.view(sim=tipping)

plt.show()