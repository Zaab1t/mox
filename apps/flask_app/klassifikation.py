from flask import Blueprint, request, render_template, g

from . update_lora import update_lora

klassifikation_side = Blueprint('klassifikation_side', __name__,
                                template_folder='templates')


@klassifikation_side.route('/klassifikation/', methods=['GET', 'POST'])
def klassifikation():
    selected_facet = ''
    selected_hovedgruppe = ''
    selected_gruppe = ''
    selected_emne = ''

    if request.method == 'POST':
        try:
            selected_facet = request.form['facetter']
            update_lora(selected_facet)
        except KeyError:
            selected_facet = ''
            update_lora(None)

        relevant_hovedgrupper = []
        relevant_grupper = []
        relevant_emner = []

        try:
            for hovedgruppe in g.hovedgrupper:
                if hovedgruppe[3] == selected_facet:
                    relevant_hovedgrupper.append(hovedgruppe)
            selected_hovedgruppe = request.form['hovedgrupper']
        except KeyError:
            pass

        if not any(selected_hovedgruppe in info_linje
                   for info_linje in relevant_hovedgrupper):
                selected_hovedgruppe = ''

        try:
            for gruppe in g.grupper:
                if gruppe[3] == selected_hovedgruppe:
                    relevant_grupper.append(gruppe)
            selected_gruppe = request.form['grupper']
        except KeyError:
            pass

        try:
            if not any(selected_gruppe in info_linje
                       for info_linje in relevant_grupper):
                selected_gruppe = ''
            for emne in g.emner:
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
            request.form['opret']
            if selected_gruppe:
                print('Opret klasse i ' + str(selected_gruppe))
                g.helper.delete_klasse_tree(selected_gruppe)
            elif selected_hovedgruppe:
                print('Opret klasse i: ' + str(selected_hovedgruppe))
            update_lora(selected_facet)
        except KeyError:
            pass

        try:
            request.form['slet']
            if selected_emne:
                print('Sletter: ' + str(selected_emne))
                g.helper.delete_klasse_tree(selected_emne,
                                            g.klasse_info)
                for emne in relevant_emner:
                    if emne[0] == selected_emne:
                        relevant_emner.remove(emne)
                selected_emne = ''
            elif selected_gruppe:
                print('Sletter: ' + str(selected_gruppe))
                g.helper.delete_klasse_tree(selected_gruppe,
                                            g.klasse_info)
                for gruppe in relevant_grupper:
                    if gruppe[0] == selected_gruppe:
                        relevant_grupper.remove(gruppe)
                relevant_emner = []
                selected_gruppe = ''
                selected_emne = ''
            elif selected_hovedgruppe:
                print('Sletter: ' + str(selected_hovedgruppe))
                g.helper.delete_klasse_tree(selected_hovedgruppe,
                                            g.klasse_info)
                for hovedgruppe in relevant_hovedgrupper:
                    if hovedgruppe[0] == selected_hovedgruppe:
                        relevant_hovedgrupper.remove(hovedgruppe)
                relevant_emner = []
                relevant_grupper = []
                selected_hovedgruppe = ''
                selected_gruppe = ''
                selected_emne = ''
            elif selected_facet:
                print('Sletter: ' + str(selected_facet))
                g.helper.delete_facet_tree(selected_facet)
                selected_facet = ''
                selected_hovedgruppe = ''
                selected_gruppe = ''
                selected_emne = ''
        except KeyError:
            pass

    else:  # Not POST
        relevant_hovedgrupper = []
        relevant_grupper = []
        relevant_emner = []
        update_lora(None)

    return render_template('klassifikation.html',
                           facetter=g.facetter,
                           hovedgrupper=relevant_hovedgrupper,
                           grupper=relevant_grupper,
                           emner=relevant_emner,
                           selected_facet=selected_facet,
                           selected_hovedgruppe=selected_hovedgruppe,
                           selected_gruppe=selected_gruppe,
                           selected_emne=selected_emne)
