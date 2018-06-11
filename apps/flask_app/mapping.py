import time
from flask import Blueprint, request, render_template, g
from . update_lora import update_lora

mapping_side = Blueprint('mapping_side', __name__,
                         template_folder='templates')


@mapping_side.route('/mapping/', methods=['GET', 'POST'])
def mapping():
    t = time.time()
    update_lora()  # This needs to be done smarter - currently very slow!
    uuid_1 = ''
    uuid_2 = ''
    mapping_return = ''
    if request.method == 'POST':
        uuid_1 = request.form['uuid_1']
        uuid_2 = request.form['uuid_2']
        map_result = g.mapper.create_mapping(uuid_1, uuid_2)
        if map_result[0]:
            mapping_return = 'Success'
        else:
            mapping_return = map_result[1]

    klasse_list = g.mapper.read_klasse_list()
    klasser = g.mapper.read_klasser(klasse_list)
    print('2: {}s'.format(time.time() - t))
    mappings = g.mapper.read_mappings(klasser)
    klasse_info = g.helper.basic_klasse_info(klasser)

    mapping_strings = []
    for klasse in klasse_info:
        if mappings[klasse['uuid']]:
            map_infos = g.helper.basic_klasse_info(mappings[klasse['uuid']])
            mapping_strings.append(klasse['bvn'] + ' ' + klasse['titel'] +
                                   ' mapper til: ' + str(map_infos))

    return render_template('mapping.html',
                           uuid_1=uuid_1,
                           uuid_2=uuid_2,
                           mapping_return=mapping_return,
                           mapping_strings=mapping_strings)
