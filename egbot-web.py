from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from search_form import SearchForm
from bfx_service import BitfinexREST
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'dasfstring'

# meaningless comment
@app.route('/', methods=['GET', 'POST'])
def egbot():
    bfx = BitfinexREST()
    bfx.load_key('.key/read-key')
    form = SearchForm()
    egbot_result = None
    egbot_header = None
    summary = None
    if form.validate_on_submit():
        start_timestamp = BitfinexREST.convert_timestamp(form.data['start_date'], form.data['start_time'])
        end_timestamp = BitfinexREST.convert_timestamp(form.data['end_date'], form.data['end_time'])
        bfx_result = bfx.get_past_trades(form.data['crypto_pair'], start_timestamp, end_timestamp)
        egbot_header = bfx_result[0].keys()
        egbot_result = [list(x.values()) for x in bfx_result]
        for x in egbot_result:
            x[2] = datetime.utcfromtimestamp(float(x[2]))
        # summary = bfx.get_summary(egbot_result)
    return render_template('base.html',
                           form=form,
                           the_egbot_header=egbot_header,
                           the_egbot_result=egbot_result,
                           the_summary=summary)


if __name__ == '__main__':
    app.run()
