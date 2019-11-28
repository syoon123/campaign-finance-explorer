from flask import Flask, render_template
import requests

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

API_KEY = "PXwofAIOrHnlY4D2tImllz22JVUiRmigH9XQwgpm"
CANDIDATES_REQUEST_URL = "https://api.open.fec.gov/v1/candidates/totals/?election_year=2020&is_active_candidate=true&min_receipts=1000000&sort=name&api_key={api_key}&sort_null_only=false&sort_hide_null=false&per_page=100".format(api_key=API_KEY)

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
    receipts = data['receipts'] + data['other_receipts']
    disbursements = data['disbursements'] + data['other_disbursements']
    totals = {
        'receipts': receipts,
        'disbursements': disbursements,
        'cash_on_hand': receipts - disbursements,
        'burn_rate': disbursements/receipts,
    }
    breakdown = {
        'big_donations': data['individual_itemized_contributions'],
        'small_donations': data['individual_unitemized_contributions'],
        'transfers': data['transfers_from_affiliated_committee'],
    }
    return {'name': candidate_name, 'totals': totals, 'breakdown': breakdown}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/presidential/')
def presidential():
    return render_template('presidential.html')

@app.route('/house/')
def house():
    return render_template('house.html')

@app.route('/house/<state>/')
def house_candidates_for_state(state):
    return render_template(state + '.html')

if __name__ == '__main__':
    app.run()
