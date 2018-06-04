from flask import Blueprint, request, render_template, g

from . update_lora import update_lora

klassifikation_side = Blueprint('klassifikation_side', __name__,
                                template_folder='templates')


@klassifikation_side.route('/klassifikation/', methods=['GET', 'POST'])
def klassifikation():
    update_lora()  # This needs to be done smarter - currently very slow!

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
            request.form['slet']
            if selected_emne:
                print('Sletter: ' + str(selected_emne))
                g.helper.delete_klasse_tree(selected_emne)
                selected_emne = ''
            elif selected_gruppe:
                print('Sletter: ' + str(selected_gruppe))
                g.helper.delete_klasse_tree(selected_gruppe)
                selected_gruppe = ''
                selected_emne = ''
            elif selected_hovedgruppe:
                print('Sletter: ' + str(selected_hovedgruppe))
                g.helper.delete_klasse_tree(selected_hovedgruppe)
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

            update_lora()
        except KeyError:
            pass

        try:
            request.form['opret']
            if selected_gruppe:
                print('Opret klasse i ' + str(selected_gruppe))
                g.helper.delete_klasse_tree(selected_gruppe)
            elif selected_hovedgruppe:
                print('Opret klasse i: ' + str(selected_hovedgruppe))
            update_lora()
        except KeyError:
            pass

    else:  # Not POST
        relevant_hovedgrupper = []
        relevant_grupper = []
        relevant_emner = []

    print(g)
    return render_template('klassifikation.html',
                           facetter=g.facetter,
                           hovedgrupper=relevant_hovedgrupper,
                           grupper=relevant_grupper,
                           emner=relevant_emner,
                           selected_facet=selected_facet,
                           selected_hovedgruppe=selected_hovedgruppe,
                           selected_gruppe=selected_gruppe,
                           selected_emne=selected_emne)
