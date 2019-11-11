from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/campaign_finance_data/<state>', methods=['GET'])
def campaign_finance_data(state):
    state = state
    return render_template('campaign_finance_data.html', state=state)


if __name__ == '__main__':
    app.run()
