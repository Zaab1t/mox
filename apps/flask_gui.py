from flask import Flask, render_template, request
from lora_helpers import LoraHelper
import settings

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


def update_lora():
    app.helper = LoraHelper(settings.host)
    klasse_list = app.helper.read_klasse_list()
    klasse_info = app.helper.basic_klasse_info(klasse_list)

    facet_list = []
    for facet_uuid in app.helper.read_facet_list():
        facet = app.helper.read_facet(facet_uuid)
        egenskaber = facet['attributter']['facetegenskaber'][0]
        info = [facet_uuid,
                egenskaber['beskrivelse'],
                egenskaber['brugervendtnoegle']]
        facet_list.append(info)
    app.facetter = facet_list

    hovedgrupper = []
    for klasse in klasse_info:
        if klasse['overklasse'] is None:
            hovedgrupper.append([klasse['uuid'],
                                 klasse['bvn'],
                                 klasse['titel'],
                                 klasse['facet']])
    app.hovedgrupper = sorted(hovedgrupper, key=lambda tup: tup[1])

    grupper = []
    for klasse in klasse_info:
        if any(klasse['overklasse'] in info_linje
               for info_linje in hovedgrupper):
            grupper.append((klasse['uuid'],
                            klasse['bvn'],
                            klasse['titel'],
                            klasse['overklasse']))
    app.grupper = sorted(grupper, key=lambda tup: tup[1])

    emner = []
    for klasse in klasse_info:
        if any(klasse['overklasse'] in info_linje
               for info_linje in grupper):
            emner.append((klasse['uuid'],
                          klasse['bvn'],
                          klasse['titel'],
                          klasse['overklasse']))
    app.emner = sorted(emner, key=lambda tup: tup[1])


@app.route('/klassifikation/', methods=['GET', 'POST'])
def hello():
    selected_facet = ''
    selected_hovedgruppe = ''
    selected_gruppe = ''
    selected_emne = ''

    if request.method == 'POST':
        try:
            selected_facet = request.form['facetter']
        except KeyError:
            selected_facet = ''

        relevant_hovedgrupper = []
        relevant_grupper = []
        relevant_emner = []

        try:
            for hovedgruppe in app.hovedgrupper:
                if hovedgruppe[3] == selected_facet:
                    relevant_hovedgrupper.append(hovedgruppe)
            selected_hovedgruppe = request.form['hovedgrupper']
        except KeyError:
            pass

        if not any(selected_hovedgruppe in info_linje
                   for info_linje in relevant_hovedgrupper):
                selected_hovedgruppe = ''

        try:
            for gruppe in app.grupper:
                if gruppe[3] == selected_hovedgruppe:
                    relevant_grupper.append(gruppe)
            selected_gruppe = request.form['grupper']
        except KeyError:
            pass

        try:
            if not any(selected_gruppe in info_linje
                       for info_linje in relevant_grupper):
                selected_gruppe = ''
            for emne in app.emner:
                if emne[3] == selected_gruppe:
                    relevant_emner.append(emne)
        except KeyError:
            pass

        try:
            selected_emne = request.form['emner']
            if not any(selected_emne in info_linje
                       for info_linje in relevant_emner):
                selected_emne = ''

        except KeyError:
            pass

        try:
            request.form['slet']
            if selected_emne:
                print('Sletter: ' + str(selected_emne))
                app.helper.delete_klasse_tree(selected_emne)
                selected_emne = ''
            elif selected_gruppe:
                print('Sletter: ' + str(selected_gruppe))
                app.helper.delete_klasse_tree(selected_gruppe)
                selected_gruppe = ''
                selected_emne = ''
            elif selected_hovedgruppe:
                print('Sletter: ' + str(selected_hovedgruppe))
                app.helper.delete_klasse_tree(selected_hovedgruppe)
                selected_hovedgruppe = ''
                selected_gruppe = ''
                selected_emne = ''
            elif selected_facet:
                print('Sletter: ' + str(selected_facet))
                app.helper.delete_facet_tree(selected_facet)
                selected_facet = ''
                selected_hovedgruppe = ''
                selected_gruppe = ''
                selected_emne = ''

            update_lora()
        except KeyError:
            pass

        try:
            request.form['opret']
            if selected_gruppe:
                print('Opret klasse i ' + str(selected_gruppe))
                app.helper.delete_klasse_tree(selected_gruppe)
            elif selected_hovedgruppe:
                print('Opret klasse i: ' + str(selected_hovedgruppe))
            update_lora()
        except KeyError:
            pass

    else:  # Not POST
        update_lora()
        relevant_hovedgrupper = []
        relevant_grupper = []
        relevant_emner = []

    return render_template('klassifikation.html',
                           facetter=app.facetter,
                           hovedgrupper=relevant_hovedgrupper,
                           grupper=relevant_grupper,
                           emner=relevant_emner,
                           selected_facet=selected_facet,
                           selected_hovedgruppe=selected_hovedgruppe,
                           selected_gruppe=selected_gruppe,
                           selected_emne=selected_emne)


if __name__ == 'flask_gui':
    update_lora()
