from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from search_form import SearchForm
from bfx_service import BitfinexREST
from datetime import datetime
from egbot_dao import EgbotDAO

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'dasfstring'


@app.route('/', methods=['GET', 'POST'])
def egbot():
    bfx = BitfinexREST()
    bfx.load_key('.key/read-key')
    form = SearchForm()
    # TODO add form functionality to select crypto and dynamically update list
    egbot_result = None
    egbot_header = None
    active_summary = None
    summary_header = None
    position = None
    position_header = None
    ticker = None
    ticker_header = None
    symbol = None
    inactive_summary = None
    inactive_summary_header = None
    dao = EgbotDAO()
    trials_dict = dao.get_all_trials_by_crypto()
    trials_list = []
    for k, v in trials_dict.items():
        for trial in v:
            str_trial = str(trial)
            str_trial = k + ': ' + str_trial
            trials_list.append((str_trial, str_trial))
    form.trial.choices = trials_list
    if form.validate_on_submit():
        crypto = form.data['trial'][0:6]
        trial_string = form.data['trial'][8:]
        trial_datetime = datetime.strptime(trial_string, '%Y-%m-%d %H:%M:%S.%f')
        orders = dao.get_order_data_for_trial(crypto, trial_datetime)
        egbot_header = orders[0].keys()
        egbot_result = [list(x.values()) for x in orders]
        for x in egbot_result:
            x[2] = datetime.utcfromtimestamp(float(x[2]))
        active_positions = bfx.get_active_positions(crypto)
        active_summary, inactive_summary = bfx.get_summary(egbot_result, active_positions, crypto)
        summary_header = active_summary.keys()
        active_summary = list(active_summary.values())
        inactive_summary_header = inactive_summary.keys()
        inactive_summary = list(inactive_summary.values())
        if active_positions:
            position_header = active_positions[0].keys()
            position = [list(x.values()) for x in active_positions]
        tick = bfx.get_ticker(crypto)
        ticker = list(tick.values())
        ticker_header = list(tick.keys())
        symbol = crypto.upper()
        symbol = symbol[0:3]
    return render_template('base.html',
                           form=form,
                           the_egbot_header=egbot_header,
                           the_egbot_result=egbot_result,
                           the_summary_header=summary_header,
                           the_summary=active_summary,
                           the_inactive_summary_header=inactive_summary_header,
                           the_inactive_summary=inactive_summary,
                           the_position_header=position_header,
                           the_position=position,
                           the_ticker=ticker,
                           the_ticker_header=ticker_header,
                           the_ticker_symbol=symbol)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
