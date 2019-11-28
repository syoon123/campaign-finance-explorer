from flask import Flask, render_template
import visualizations
from bokeh.embed import components

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/presidential/')
def presidential():
    cash_on_hand_plot = visualizations.cash_on_hand_stacked_bar_graph('P')
    cash_on_hand_script, cash_on_hand_div = components(cash_on_hand_plot)
    return render_template('presidential.html',
                           cash_on_hand_script=cash_on_hand_script,
                           cash_on_hand_div=cash_on_hand_div)


@app.route('/house/')
def house():
    return render_template('house.html')


@app.route('/house/<state>/')
def house_candidates_for_state(state):
    return render_template(state + '.html')


if __name__ == '__main__':
    app.run()
