import matplotlib.pyplot as plt
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import os
from matplotlib import cm 

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
PLOTS_FOLDER = os.path.join(CURRENT_FOLDER, "plots")
if not os.path.exists(PLOTS_FOLDER):
    os.makedirs(PLOTS_FOLDER)

class SimpleAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
        norm_id = self.unique_id / model.num_agents
        self.color = cm.viridis(norm_id) 

    def step(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

class SimpleModel(Model):
    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.current_step = 0
        
        self.datacollector = DataCollector(
            agent_reporters={"Position": lambda a: a.pos}
        )
        
        for i in range(self.num_agents): 
            a = SimpleAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle().do("step")
        self.current_step += 1
        
        if self.current_step % 10 == 0:
            print(f"Step {self.current_step} completed. Agents moved.")

    def run_model(self, steps):
        for _ in range(steps):
            self.step()

def get_data(model, start=False):
    x_coords = []
    y_coords = []
    colors = []

    data = model.datacollector.get_agent_vars_dataframe()
    
    if "Step" in data.index.names:
        step_index = data.index.get_level_values('Step').min() if start else data.index.get_level_values('Step').max()
        positions = data.xs(step_index, level="Step")["Position"]
        
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
    else: 
        for agent in model.agents:
            x_coords.append(agent.pos[0])
            y_coords.append(agent.pos[1])
        step_index = 0

    for agent in model.agents:
        colors.append(agent.color)
    
    return x_coords, y_coords, colors, step_index

def plot_positions(x, y, colors, step_num, grid_width, grid_height):
    plt.figure(figsize=(8, 8))
    plt.scatter(x, y, c=colors, alpha=0.8, s=150, edgecolors='black') 
    plt.xlim(0, grid_width)
    plt.ylim(0, grid_height)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(f"Positions {len(x)} agents at step {step_num}")
    filename = os.path.join(PLOTS_FOLDER, f"agent_positions_step_{step_num}.png")
    plt.savefig(filename)
    print(f"Plot saved to {filename}")
    plt.show()
    plt.close()

if __name__ == "__main__":
    WIDTH = 20
    HEIGHT = 20
    AGENTS = 50
    STEPS = 100

    print(f"=== Creating Model with {AGENTS} agents on Grid {WIDTH}*{HEIGHT} ===")
    model = SimpleModel(AGENTS, WIDTH, HEIGHT)
    
    print(f"=== Performing {STEPS} steps ===")
    model.run_model(STEPS)

    print(f"=== Getting initial positions ===")
    x_start, y_start, colors_start, start_step = get_data(model, start=True) 
    plot_positions(x_start, y_start, colors_start, start_step, WIDTH, HEIGHT)

    print(f"=== Getting final positions ===")
    x_end, y_end, colors_end, last_step = get_data(model, start=False) 
    plot_positions(x_end, y_end, colors_end, last_step, WIDTH, HEIGHT)