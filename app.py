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



if __name__ == '__main__':
    app.run()
