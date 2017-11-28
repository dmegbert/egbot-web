from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from search_form import SearchForm
from bfx_service import BitfinexREST
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'dasfstring'


@app.route('/', methods=['GET', 'POST'])
def egbot():
    bfx = BitfinexREST()
    bfx.load_key('.key/read-key')
    form = SearchForm()
    egbot_result = None
    egbot_header = None
    summary = None
    summary_header = None
    position = None
    position_header = None
    ticker = None
    ticker_header = None
    if form.validate_on_submit():
        start_timestamp = BitfinexREST.convert_timestamp(form.data['start_date'], form.data['start_time'])
        end_timestamp = BitfinexREST.convert_timestamp(form.data['end_date'], form.data['end_time'])
        bfx_result = bfx.get_past_trades(form.data['crypto_pair'], start_timestamp, end_timestamp)
        egbot_header = bfx_result[0].keys()
        egbot_result = [list(x.values()) for x in bfx_result]
        for x in egbot_result:
            x[2] = datetime.utcfromtimestamp(float(x[2]))
        active_positions = bfx.get_active_positions()
        summary = bfx.get_summary(egbot_result, active_positions, form.data['crypto_pair'])
        summary_header = summary.keys()
        summary = list(summary.values())
        position_header = active_positions[0].keys()
        position = [list(x.values()) for x in active_positions]
        tick = bfx.get_ticker(form.data['crypto_pair'])
        ticker = list(tick.values())
        ticker_header = list(tick.keys())
    return render_template('base.html',
                           form=form,
                           the_egbot_header=egbot_header,
                           the_egbot_result=egbot_result,
                           the_summary_header=summary_header,
                           the_summary=summary,
                           the_position_header=position_header,
                           the_position=position,
                           the_ticker=ticker,
                           the_ticker_header=ticker_header)


if __name__ == '__main__':
    app.run()
