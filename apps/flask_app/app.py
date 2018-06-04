from flask import Flask

from . hello import simple_page
from . klassifikation import klassifikation_side
from . mapping import mapping_side

app = Flask(__name__)
app.register_blueprint(simple_page)
app.register_blueprint(klassifikation_side)
app.register_blueprint(mapping_side)
