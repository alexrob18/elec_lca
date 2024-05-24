# %%
import bw2io as bi
import bw2data as bd
#import bw2calc as bc
#from bw_graph_tools import NewNodeEachVisitGraphTraversal
#import pandas as pd
import panel as pn
#import elec_lca
import plotly.graph_objs as go

#https://panel.holoviz.org/developer_guide/extensions.html#extension-plugins
pn.extension()

# BRIGHTWAY SETUP ###############################################################

'''
def check_for_brightway_project():
    if 'bw2_spring_school' not in bd.projects:
        bi.install_project(project_key='bw2_spring_school', overwrite_existing=True)
    bd.projects.set_current(name='bw2_spring_school')
    db = bd.Database('ecoinvent_updated_electricity_mix_CA-QC')
    return db

db = check_for_brightway_project()
'''

# IMPORT DATA ###################################################################

df_scenarios = pd.read_excel()
#elec_lca.reading.read_user_input_template_excel_file('../data', 'user_input_template.xlsm')

# PANEL SETUP ###################################################################

widget_button_BAU = pn.widgets.Button(
    name='BAU scenario',
    button_type='primary'
)

widget_button_NZ50 = pn.widgets.Button(
    name='NZ50 scenario',
    button_type='success'
)


def stacked_area_chart(scenario):

    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(layout=layout)
    df_scenario = df_scenarios[df_scenarios.scenario == scenario]
    df_scenario = df_scenario.sort_values(by=['period'])
    tech_list = list(df_scenario.technology.unique())
    t = list(df_scenario.period.unique())

    for tech in tech_list:
        data = list(100 * df_scenario[df_scenario.technology == tech].value)
        fig.add_trace(go.Scatter(
            x=t, y=data,
            # hoverinfo='x+y',
            mode='lines',
            name=tech,
            # line=dict(width=0.5, color='rgb(131, 90, 241)'),
            stackgroup='one'  # define stack group
        ))

    fig.update_layout(
        xaxis_title="Years",
        yaxis_title="Shares [%]",
        legend_title="Technologies",
    )

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")

    return fig

widget_plotly = pn.pane.Plotly(fig=stacked_area_chart("NZ50"))
pn.pane.Plotly(fig=stacked_area_chart("NZ50"))

# INTERACTIVE ELEMENTS #######################################################

def update_interactive_elements(scenario):
    fig = stacked_area_chart(scenario)
    widget_plotly.fig = fig




# https://panel.holoviz.org/reference/widgets/Button.html#buttonhttps://panel.holoviz.org/reference/widgets/Button.html#button
widget_button_BAU.on_click(update_interactive_elements(scenario='BAU'))
widget_button_NZ50.on_click(update_interactive_elements(scenario='NZ50'))

# https://panel.holoviz.org/reference/layouts/Column.html
pn.Column(
    widget_button_BAU,
    widget_button_NZ50,
    widget_plotly,
).servable()