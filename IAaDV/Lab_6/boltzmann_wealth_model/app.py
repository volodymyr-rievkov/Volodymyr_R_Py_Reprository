import altair as alt

from model import BoltzmannWealth
from mesa.mesa_logging import INFO, log_to_stderr
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

log_to_stderr(INFO)


def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color=agent.wealth
    ) 


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}


def post_process(chart):
    chart = chart.encode(
        color=alt.Color(
            "color:N",
            scale=alt.Scale(scheme="viridis", domain=[0, 10]),
            legend=alt.Legend(
                title="Wealth",
                orient="right",
                type="gradient",
                gradientLength=200,
            ),
        ),
    )
    return chart


model = BoltzmannWealth(50, 10, 10, mode=3)

renderer = SpaceRenderer(model, backend="altair")

renderer.draw_structure(grid_color="black", grid_dash=[6, 2], grid_opacity=0.3)
renderer.draw_agents(agent_portrayal=agent_portrayal, cmap="viridis", vmin=0, vmax=10)

renderer.post_process = post_process

GiniPlot = make_plot_component("Gini")

page = SolaraViz(
    model,
    renderer,
    components=[GiniPlot],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)

