import os
from peak.tools import logging
from peak.tools.logging import PeakLogger
from dash import Dash, html

logger: PeakLogger = logging.get_logger()

app = Dash(__name__)

app.layout = html.Div([
    html.Div(children='Hello World')
])

if __name__ == '__main__':
    logger.bind(context={'test_key': os.getenv("TENANT_NAME")})
    logger.info("Creating a dash Hello World App!")
    app.run_server(debug=True)
