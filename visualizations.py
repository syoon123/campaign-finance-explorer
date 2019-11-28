import requests
import math

from bokeh.models import HoverTool, NumeralTickFormatter
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.transform import cumsum
import pandas as pd

API_KEY = "PXwofAIOrHnlY4D2tImllz22JVUiRmigH9XQwgpm"
CANDIDATES_REQUEST_URL = "https://api.open.fec.gov/v1/candidates/totals/?election_year=2020&is_active_candidate=true&min_receipts=1000000&sort=receipts&api_key={api_key}&sort_null_only=false&sort_hide_null=false&per_page=100".format(api_key=API_KEY)


def get_candidates(office, state=None, party=None):
    """
    Params: office ('P', 'H', or 'S'), party ('DEM', 'REP' or None),  state ('NY', 'MA', etc. or None)
    Returns: dictionary with candidate IDs as keys and their names as values
    """
    url = CANDIDATES_REQUEST_URL + "&office={o}".format(o=office)
    if state is not None:
        url += "&state={s}".format(s=state)
    if party is not None:
        url += "&party={p}".format(p=party)
    data = requests.get(url).json()
    candidates = {}
    url += "&page=0"
    for page in range(int(data['pagination']['pages'])):
        url= url[:-1] + str(page+1)
        candidate_data = requests.get(url).json()['results']
        for candidate in candidate_data:
            name = candidate['name']
            candidate_id = candidate['candidate_id']
            candidates[candidate_id] = name
    return candidates


def get_campaign_finance_data(candidate_id, candidate_name):
    """
    Params: candidate_id
    Returns: dictionary with candidate's name and totals (receipts, disbursements, and cash on hand)
    """
    url = "https://api.open.fec.gov/v1/candidate/{cand_id}/totals/?page=1&sort_null_only=false&sort_nulls_last=false&cycle=2020&api_key={api_key}&sort=-cycle&per_page=20&sort_hide_null=false".format(api_key=API_KEY, cand_id=candidate_id)
    data = requests.get(url).json()['results'][0]
    receipts = int((data['receipts'] + data['other_receipts']) * 100) / 100
    disbursements = int((data['disbursements'] + data['other_disbursements']) * 100) / 100
    if receipts == 0:
        burn_rate = 0.0
    else:
        burn_rate = disbursements/receipts
    totals = {
        'receipts': receipts,
        'disbursements': disbursements,
        'cash_on_hand': receipts - disbursements,
        'burn_rate': burn_rate
    }
    breakdown = {
        'big_donations': int(data['individual_itemized_contributions'] * 100) / 100,
        'small_donations': int(data['individual_unitemized_contributions'] * 100) / 100,
        'transfers': int(data.get('transfers_from_affiliated_committee', 0.0) * 100) / 100 
    }
    return {'name': candidate_name, 'totals': totals, 'breakdown': breakdown}


def cash_on_hand_stacked_bar_graph(office, state=None, party=None):
    candidates = get_candidates(office, state, party)
    data = {'candidate_names': [],
            'Cash on hand': [],
            'Disbursements': [],}
    for candidate_id in candidates:
        try:
            candidate_data = get_campaign_finance_data(candidate_id, candidates[candidate_id])
            data['candidate_names'].append(candidate_data['name'])
            data['Cash on hand'].append(candidate_data['totals']['cash_on_hand'])
            data['Disbursements'].append(candidate_data['totals']['disbursements'])
        except:
            continue
    portions = ['Cash on hand', 'Disbursements']
    colors = ["#32752a", "#748073"]
    plot = figure(x_range=data['candidate_names'],
                  plot_height=600,
                  plot_width=700,
                  title="Money Raised/Spent by Each Candidate",
                  toolbar_location=None,
                  tools="hover",
                  tooltips="$name @candidate_names: @$name{($ 0,0.00)}")
    plot.vbar_stack(portions,
                    x='candidate_names',
                    width=0.9, color=colors, source=data, legend_label=portions)
    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = math.pi/2
    plot.xgrid.grid_line_color = None
    plot.yaxis.formatter.use_scientific = False
    plot.axis.minor_tick_line_color = None
    plot.outline_line_color = None
    plot.legend.location = "top_left"
    plot.legend.orientation = "horizontal"
    return plot


def burn_rate_bar_graph(office, state=None, party=None):
    candidates = get_candidates(office, state, party)
    data = {'candidate_names': [],
            'Burn Rate': [],}
    for candidate_id in candidates:
        try:
            candidate_data = get_campaign_finance_data(candidate_id, candidates[candidate_id])
            data['candidate_names'].append(candidate_data['name'])
            data['Burn Rate'].append(candidate_data['totals']['burn_rate'])
        except:
            continue
    plot = figure(x_range=data['candidate_names'],
                  plot_height=600,
                  plot_width=700,
                  title="Burn Rates for Each Candidate",
                  toolbar_location=None,
                  tools="hover",
                  tooltips="Burn rate for @candidate_names: @{Burn Rate}{(0.0 %)}")
    plot.vbar(x='candidate_names', top='Burn Rate', width=0.9, fill_color='#f55f3d', line_color="#f55f3d", source=data)
    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = math.pi/2
    plot.xgrid.grid_line_color = None
    plot.yaxis.formatter = NumeralTickFormatter(format='0.0 %')
    plot.axis.minor_tick_line_color = None
    plot.outline_line_color = None
    return plot


def candidate_funding_pie_chart(candidate_id):
    url = "https://api.open.fec.gov/v1/candidate/{cand_id}/?page=1&sort_null_only=false&sort_nulls_last=false&api_key={api_key}&sort_hide_null=false".format(api_key=API_KEY, cand_id=candidate_id)
    candidate_name = requests.get(url).json()['results'][0]['name']
    candidate_party = requests.get(url).json()['results'][0]['party']
    data = get_campaign_finance_data(candidate_id, candidate_name)
    total_receipts = data['totals']['receipts']
    x = {
        'Big Donations': data['breakdown']['big_donations'],
        'Small Donations': data['breakdown']['small_donations'],
        'Transfers': data['breakdown']['transfers'],
    }
    x['Other'] = total_receipts - \
       (x['Big Donations'] + x['Small Donations'] + x['Transfers'])
    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'portion'})
    data['angle'] = data['value']/data['value'].sum() * 2* math.pi
    data['color'] = ["#D55E00","#0072B2", "#F0E442", "#009E73"]
    plot = figure(plot_height=600, plot_width=700,
                  title="", toolbar_location=None,
                  tools="hover", tooltips="@portion: $@value{0.00}", x_range=(-0.5, 1.0))
    plot.wedge(x=0.1, y=0.1, radius=0.5,
               start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
               line_color="white", fill_color='color',
               legend_field='portion',
               source=data)
    plot.axis.axis_label=None
    plot.axis.visible=False
    plot.grid.grid_line_color = None
    return candidate_name, candidate_party, total_receipts, plot
    
