from flask import Flask, render_template, request
import visualizations
from bokeh.embed import components

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

    
@app.route('/presidential/')
def presidential():
    p = request.args.get('party')
    cash_on_hand_plot = visualizations.cash_on_hand_stacked_bar_graph('P', party=p)
    cash_on_hand_script, cash_on_hand_div = components(cash_on_hand_plot)
    return render_template('receipts.html',
                           campaign_type='Presidential',
                           base='/presidential',
                           cash_on_hand_script=cash_on_hand_script,
                           cash_on_hand_div=cash_on_hand_div)


@app.route('/presidential/burnrates/')
def presidential_burn_rates():
    p = request.args.get('party')
    burn_rates_plot = visualizations.burn_rate_bar_graph('P', party=p)
    burn_rates_script, burn_rates_div = components(burn_rates_plot)
    return render_template('burnrates.html',
                           campaign_type='Presidential',
                           base='/presidential',
                           burn_rates_script=burn_rates_script,
                           burn_rates_div=burn_rates_div)


@app.route('/house/')
def house():
    return render_template('house.html')


@app.route('/house/<state>/')
def house_candidates_for_state(state):
    p = request.args.get('party')
    cash_on_hand_plot = visualizations.cash_on_hand_stacked_bar_graph('H', state=state, party=p)
    cash_on_hand_script, cash_on_hand_div = components(cash_on_hand_plot)
    return render_template('receipts.html',
                           campaign_type='House',
                           state=state,
                           base='/house/{s}'.format(s=state),
                           cash_on_hand_script=cash_on_hand_script,
                           cash_on_hand_div=cash_on_hand_div)


@app.route('/house/<state>/burnrates/')
def house_burn_rates(state):
    p = request.args.get('party')
    burn_rates_plot = visualizations.burn_rate_bar_graph('H', state=state, party=p)
    burn_rates_script, burn_rates_div = components(burn_rates_plot)
    return render_template('burnrates.html',
                           campaign_type='House',
                           state=state,
                           base='/house/{s}'.format(s=state),
                           burn_rates_script=burn_rates_script,
                           burn_rates_div=burn_rates_div)


@app.route('/senate/')
def senate():
    return render_template('senate.html')


@app.route('/senate/<state>/')
def senate_candidates_for_state(state):
    p = request.args.get('party')
    cash_on_hand_plot = visualizations.cash_on_hand_stacked_bar_graph('S', state=state, party=p)
    cash_on_hand_script, cash_on_hand_div = components(cash_on_hand_plot)
    return render_template('receipts.html',
                           campaign_type='Senate',
                           state=state,
                           base='/senate/{s}'.format(s=state),
                           cash_on_hand_script=cash_on_hand_script,
                           cash_on_hand_div=cash_on_hand_div)


@app.route('/senate/<state>/burnrates/')
def senate_burn_rates(state):
    p = request.args.get('party')
    burn_rates_plot = visualizations.burn_rate_bar_graph('S', state=state, party=p)
    burn_rates_script, burn_rates_div = components(burn_rates_plot)
    return render_template('burnrates.html',
                           campaign_type='Senate',
                           state=state,
                           base='/senate/{s}'.format(s=state),
                           burn_rates_script=burn_rates_script,
                           burn_rates_div=burn_rates_div)


@app.route('/<office>/candidates/<candidate_id>', defaults={'state': None})
@app.route('/<office>/<state>/candidates/<candidate_id>')           
def individual_candidate(office, state, candidate_id):
    name, party, total_receipts, plot = visualizations.candidate_funding_pie_chart(candidate_id)
    funding_pie_script, funding_pie_div = components(plot)
    campaign_type=office[0].upper() + office[1:]
    if state is None:
        return render_template('candidate.html',
                               candidate_name=name,
                               candidate_party=party,
                               candidate_total_receipts=total_receipts,
                               campaign_type=campaign_type,
                               base='/{office}'.format(office=office),
                               funding_pie_script=funding_pie_script,
                               funding_pie_div=funding_pie_div)
    return render_template('candidate.html',
                           candidate_name=name,
                           candidate_party=party,
                           candidate_total_receipts=total_receipts,
                           campaign_type=campaign_type,
                           state=state,
                           base='/{office}/{state}'.format(office=office, state=state),
                           funding_pie_script=funding_pie_script,
                           funding_pie_div=funding_pie_div)
                           


if __name__ == '__main__':
    app.run()
