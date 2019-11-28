import requests
import math

from bokeh.models import HoverTool, NumeralTickFormatter
from bokeh.io import show, output_file
from bokeh.plotting import figure

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
    Params: candidate_id, candidate_name
    Returns: dictionary with candidate's totals (receipts, disbursements, and cash on hand)
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

