import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import pandas as pd

INPUT_FILE = 'D:/Programming/PythonApplications/IAaDV/Lab_7/survey_results.csv'

def create_fuzzy_system():

    hard_skills = ctrl.Antecedent(np.arange(0, 11, 1), 'HardSkills')
    soft_skills = ctrl.Antecedent(np.arange(0, 11, 1), 'SoftSkills')
    reliability = ctrl.Antecedent(np.arange(0, 11, 1), 'Reliability')

    compatibility = ctrl.Consequent(np.arange(0, 101, 1), 'Compatibility')

    hard_skills.automf(3)  
    soft_skills.automf(3)
    reliability.automf(3)

    compatibility['low'] = fuzz.trimf(compatibility.universe, [0, 0, 40])
    compatibility['medium'] = fuzz.trimf(compatibility.universe, [30, 50, 70])
    compatibility['high'] = fuzz.trimf(compatibility.universe, [60, 80, 100])
    compatibility['perfect'] = fuzz.trimf(compatibility.universe, [85, 100, 100])

    rule1 = ctrl.Rule(reliability['poor'], compatibility['low'])
    
    rule2 = ctrl.Rule(hard_skills['poor'] | soft_skills['poor'], compatibility['low'])
    
    rule3 = ctrl.Rule(hard_skills['average'] & soft_skills['average'], compatibility['medium'])
    
    rule4 = ctrl.Rule(hard_skills['good'] & reliability['good'], compatibility['high'])
    
    rule5 = ctrl.Rule(hard_skills['good'] & soft_skills['good'] & reliability['good'], compatibility['perfect'])

    scoring_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
    simulation = ctrl.ControlSystemSimulation(scoring_ctrl)

    return simulation

def process_data(simulation):

    try:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        
        if len(df.columns) >= 5:
            df.columns = ['Timestamp', 'Name', 'HardSkills', 'SoftSkills', 'Reliability']
        
        results = []
        
        for index, row in df.iterrows():
            simulation.input['HardSkills'] = row['HardSkills']
            simulation.input['SoftSkills'] = row['SoftSkills']
            simulation.input['Reliability'] = row['Reliability']
            
            simulation.compute()
            results.append(simulation.output['Compatibility'])

        df['Compatibility_Score'] = results
        
        df_sorted = df.sort_values(by='Compatibility_Score', ascending=False)
        return df_sorted

    except FileNotFoundError:
        print("Помилка: Файл survey_data.csv не знайдено.")
        return None
    except Exception as e:
        print(f"Критична помилка: {e}")
        return None

def plot_graph(df):
    plt.figure(figsize=(12, 6))
    
    bars = plt.bar(df['Name'], df['Compatibility_Score'], color='teal', alpha=0.7)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1, 
                 f'{height:.1f}', ha='center', va='bottom', fontsize=9)

    plt.xlabel('Кандидати')
    plt.ylabel('Сумісність (%)')
    plt.title('Рейтинг сумісності кандидатів (Fuzzy Logic)')
    plt.xticks(rotation=45) 
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def main():
    print("--- Початок роботи ---")
    
    sim = create_fuzzy_system()
    
    df_result = process_data(sim)
    
    if df_result is not None:
        print("\n=== ТОП-3 КАНДИДАТИ ===")
        print(df_result[['Name', 'Compatibility_Score']].head(3).to_string(index=False))

        plot_graph(df_result)

if __name__ == "__main__":
    main()