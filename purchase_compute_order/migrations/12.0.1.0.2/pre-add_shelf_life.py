def migrate(cr, version):
    if not version:
        return
    cr.execute('''
        ALTER TABLE computed_purchase_order_line ADD COLUMN shelf_life INTEGER
    ''')
    return
