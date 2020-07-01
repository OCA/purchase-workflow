def migrate(cr, version):
    if not version:
        return
    cr.execute('''
        update res_partner p set target_type ='weight'
        where target_type ='weight_net'
    ''')
    return
