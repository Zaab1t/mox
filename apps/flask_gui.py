from flask import Flask, render_template, request
from lora_helpers import LoraHelper
import settings

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

lora_hostname = settings.host
helper = LoraHelper(settings.host)
klasse_list = helper.read_klasse_list()
klasse_info = helper.basic_klasse_info(klasse_list)

hovedgrupper = []
for klasse in klasse_info:
    if klasse['overklasse'] is None:
        hovedgrupper.append([klasse['uuid'], klasse['bvn'], klasse['titel']])
app.hovedgrupper = sorted(hovedgrupper, key=lambda tup: tup[1])

grupper = []
for klasse in klasse_info:
    if any(klasse['overklasse'] in info_linje for info_linje in hovedgrupper):
        grupper.append((klasse['uuid'], klasse['bvn'],
                        klasse['titel'], klasse['overklasse']))
app.grupper = sorted(grupper, key=lambda tup: tup[1])

emner = []
for klasse in klasse_info:
    if any(klasse['overklasse'] in info_linje for info_linje in grupper):
        emner.append((klasse['uuid'], klasse['bvn'],
                      klasse['titel'], klasse['overklasse']))
app.emner = sorted(emner, key=lambda tup: tup[1])


@app.route('/klassifikation/', methods=['GET', 'POST'])
def hello():
    selected_hovedgruppe = ''
    selected_gruppe = ''
    selected_emne = ''

    if request.method == 'POST':
        selected_hovedgruppe = request.form['hovedgrupper']

        relevant_grupper = []
        relevant_emner = []
        for gruppe in app.grupper:
            if gruppe[3] == selected_hovedgruppe:
                relevant_grupper.append(gruppe)

        try:
            selected_gruppe = request.form['grupper']
            print(selected_gruppe)
            for emne in app.emner:
                if emne[3] == selected_gruppe:
                    relevant_emner.append(emne)
        except KeyError:
            pass

        try:
            selected_emne = request.form['emner']
        except KeyError:
            pass
    else:
        relevant_grupper = []
        relevant_emner = []

    return render_template('klassifikation.html',
                           hovedgrupper=app.hovedgrupper,
                           grupper=relevant_grupper,
                           emner=relevant_emner,
                           selected_hovedgruppe=selected_hovedgruppe,
                           selected_gruppe=selected_gruppe,
                           selected_emne=selected_emne)
