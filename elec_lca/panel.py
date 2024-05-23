import panel as pn
import pandas as pd

pn.extension()

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
widget_text_input_load = pn.widgets.TextInput(
    placeholder='Enter the path where the input Excel file is located here...'
)
widget_select_scn = pn.widgets.Select(
    name='Scenario Name',
    options=["BAU", "NZ50"]
)
widget_select_start_year = pn.widgets.Select(
    name='Start Year',
    options=[2020, 2021, 2022]
)
widget_select_end_year = pn.widgets.Select(
    name='End Year',
    options=[2020, 2021, 2022]
)
multi_select_location = pn.widgets.MultiSelect(
    name='Location',
    options=["QC", "NB"]
)
widget_button_show_data = pn.widgets.Button(
    name='Show Input Data',
    button_type='primary'
)
widget_button_calculate_lca = pn.widgets.Button(
    name='Calculate LCA',
    button_type='primary'
)
df = pd.DataFrame({
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
    'bool': [True, False, True],
}, index=[1, 2, 3])
widget_df_input_data = pn.widgets.DataFrame(df, name='Inputs', sizing_mode='stretch_both')
widget_df_results = pn.widgets.DataFrame(df, name='Results', sizing_mode='stretch_both')

gspec = pn.GridSpec(sizing_mode='stretch_both', max_height=800)

row1 = pn.Row(widget_button_create_input_file, widget_text_input_create,  sizing_mode='stretch_width')
row2 = pn.Row(widget_button_load_input_file, widget_text_input_load,  sizing_mode='stretch_width')

gspec[:,   0] = pn.Column(
    row1,
    row2,
    widget_select_scn,
    multi_select_location,
    widget_select_start_year,
    widget_select_end_year,
    widget_button_show_data,
    widget_button_calculate_lca
)

gspec[0, 1:2] = widget_df_input_data
gspec[1, 1] = widget_df_results
gspec[1, 2] = pn.Spacer(styles=dict(background='purple'))

gspec.servable()