from flask import Flask, escape, request, render_template
import requests
import json
import os


FUNC_URL = os.getenv('FUNC_URL')
INST_KEY= "InstrumentationKey=" + os.getenv('INSTRUMENTATION_KEY')


app = Flask(__name__)


# ##############################
# Trace

from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

# for dependencies. Check Application Insights 'dependencies' and 'requests'
#   requests: incoming requests
#   dependencies: outgoing requests
# Sampling Rate is 100%
tracer = Tracer(
    exporter=AzureExporter(
        connection_string=INST_KEY),
    sampler=ProbabilitySampler(1.0),
)

from opencensus.ext.flask.flask_middleware import FlaskMiddleware
# for requests
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(
        connection_string=INST_KEY),
    sampler=ProbabilitySampler(rate=1.0),
)


# ##############################
# Metrics
from datetime import datetime
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

prompt_measure = measure_module.MeasureInt("prompt",
                                        "number of prompts",
                                        "prompts")
prompt_view = view_module.View("prompt view",
                               "number of prompts",
                               [],
                               prompt_measure,
                               aggregation_module.CountAggregation())
view_manager.register_view(prompt_view)
mmap = stats_recorder.new_measurement_map()
tmap = tag_map_module.TagMap()
exporter = metrics_exporter.new_metrics_exporter(
    connection_string=INST_KEY)

view_manager.register_exporter(exporter)
mmap.measure_int_put(prompt_measure, 1)
mmap.record(tmap)


# ##############################
# Logs
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
logger = logging.getLogger(__name__)
#format_str = '%(asctime)s - %(levelname)-8s - traceId=%(operation_Id) spanId=%(spanId) %(message)s'
format_str = '%(asctime)s - %(levelname)-8s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(format_str, date_format)

handler = AzureLogHandler(connection_string=INST_KEY)
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.route('/log')
def logmsg():
    msg = request.args.get("msg")
    logger.error(msg)
    logger.warning(msg)
    logger.info(msg)
    logger.debug(msg)

    return msg


@app.route('/')
def index():
    with tracer.span(name="index") as span:
        return "Hello Tracing!"

@app.route('/get')
def getItem():
    logger.warning(request.headers.get("traceparent"))
    logger.warning("BEFORE THE SPAN")
    with tracer.span(name="get") as span:
        logging.warning("IN THE SPAN: spanId=" + span.span_id + ", parentSpanId=" + span.parent_span.span_id)
        id = request.args.get("id")

        headers = {'content-type': 'application/json'}
        payload = {'id': id}
        r = requests.post(FUNC_URL + '/api/GetToDo', headers = headers, data=json.dumps(payload))

    logger.warning("AFTER THE SPAN")
    return render_template("todoItemView.html", todo=r.json())

@app.route('/list')
def listItems():
    with tracer.span(name="list") as span:
        logging.warning("IN THE SPAN: spanId=" + span.span_id + ", parentSpanId=" + span.parent_span.span_id)

        r = requests.post(FUNC_URL + '/api/ListToDo')

        return render_template("todoItemList.html", list=r.json())

@app.route('/put')
def putItem():
    return "put"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
