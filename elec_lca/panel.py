import panel as pn
import pandas as pd
import plotly.graph_objs as go
from elec_lca import Elec_LCA
from caching import load_db

database = load_db(r"C:\myprojects\SpringSchool\ei391.pickle")

elec_obj = Elec_LCA(database, "TRACI v2.1")


def stacked_area_chart(df_scenario, col):

    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(layout=layout)
    df_scenario = df_scenario.sort_values(by=['period'])
    tech_list = list(df_scenario[col].unique())
    t = list(df_scenario.period.unique())

    for tech in tech_list:
        data = list(100 * df_scenario[df_scenario[col] == tech].value)
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


pn.extension('plotly')


# PANEL SETUP ###################################################################

widget_button_create_input_file = pn.widgets.Button(
    name='Create Input File',
    button_type='primary',
)
widget_text_input_create = pn.widgets.TextInput(
    placeholder='Enter the path to write the input Excel file here...'
)
widget_button_load_input_file = pn.widgets.Button(
    name='Load Input File',
    button_type='primary',
)
widget_select_scn = pn.widgets.Select(
    name='Scenario Name',
)
widget_select_start_year = pn.widgets.Select(
    name='Start Year',
)
widget_select_end_year = pn.widgets.Select(
    name='End Year',
)
widget_select_location = pn.widgets.Select(
    name='Location',
)
widget_button_show_data = pn.widgets.Button(
    name='Show Input Data',
    button_type='primary'
)
widget_button_calculate_lca = pn.widgets.Button(
    name='Calculate LCA',
    button_type='primary'
)
df_scenarios = pd.DataFrame()
df = pd.DataFrame()
widget_df_input_data = pn.widgets.DataFrame(df_scenarios, name='Inputs', sizing_mode='stretch_both')
widget_plotly_pane_input = pn.pane.Plotly(sizing_mode='stretch_both')
widget_df_results = pn.widgets.DataFrame(df, name='Results', sizing_mode='stretch_both')
widget_plotly_pane_results = pn.pane.Matplotlib(sizing_mode='stretch_both')

gspec = pn.GridSpec(sizing_mode='stretch_both', max_height=800)

row1 = pn.Row(widget_button_create_input_file, widget_text_input_create,  sizing_mode='stretch_width')
row2 = pn.Row(widget_button_load_input_file,  sizing_mode='stretch_width')

gspec[:,   0] = pn.Column(
    row1,
    row2,
    widget_select_scn,
    widget_select_location,
    widget_select_start_year,
    widget_select_end_year,
    widget_button_show_data,
    widget_button_calculate_lca
)

gspec[0, 1] = widget_df_input_data
gspec[0, 2] = widget_plotly_pane_input
gspec[1, 1] = widget_df_results
gspec[1, 2] = widget_plotly_pane_results

# INTERACTIVE ELEMENTS #######################################################


def create_input_file(event):
    filepath = widget_text_input_create.value
    elec_obj.create_input_file(filepath)


widget_button_create_input_file.on_click(create_input_file)


def load_input_file(event):
    elec_obj.load_user_input_file()
    elec_obj.create_new_location_dataset()
    df_scns = elec_obj.df_scenario
    list_scns = df_scns["scenario"].unique().tolist()
    widget_select_scn.options = list_scns
    list_period = df_scns["period"].unique().tolist()
    widget_select_start_year.options = list_period
    widget_select_end_year.options = list_period
    list_location = df_scns["location"].unique().tolist()
    widget_select_location.options = list_location


widget_button_load_input_file.on_click(load_input_file)


def show_inputs(event):
    scenario = widget_select_scn.value
    start_year = widget_select_start_year.value
    end_year = widget_select_end_year.value
    location = widget_select_location.value
    df_scns = elec_obj.df_scenario
    df_scns = df_scns[df_scns["scenario"] == scenario].copy()
    df_scns = df_scns[(df_scns["period"] >= start_year) & (df_scns["period"] <= end_year)].copy()
    df_scns = df_scns[df_scns["location"] == location].copy()
    widget_df_input_data.value = df_scns
    widget_plotly_pane_input.object = stacked_area_chart(df_scns, "technology")


widget_button_show_data.on_click(show_inputs)


def show_results(event):
    elec_obj.compute_lca_score_for_all_scenario()
    scenario = widget_select_scn.value
    start_year = widget_select_start_year.value
    end_year = widget_select_end_year.value
    location = widget_select_location.value
    df_results = elec_obj.df_results
    df_results = df_results[df_results["scenario"] == scenario].copy()
    df_results = df_results[(df_results["period"] >= start_year) & (df_results["period"] <= end_year)].copy()
    df_results = df_results[df_results["location"] == location].copy()
    widget_df_results.value = df_results
    elec_obj.create_plot_for_1_loc(location, scenario)
    widget_plotly_pane_results.object = elec_obj.results_fiure


widget_button_calculate_lca.on_click(show_results)

gspec.servable()
