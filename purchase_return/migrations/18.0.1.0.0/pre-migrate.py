def convert_text_to_html(cr):
    cr.execute("""
        SELECT id, notes FROM purchase_return_order
        WHERE notes IS NOT NULL
    """)
    rows = cr.fetchall()

    for rec_id, notes in rows:
        if notes:
            notes_html = (
                notes.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            notes_html = "<p>" + notes_html.replace("\n", "</p><p>") + "</p>"
            cr.execute(
                """
                UPDATE purchase_return_order
                SET notes=%s
                WHERE id=%s
            """,
                (notes_html, rec_id),
            )


def migrate(cr, version):
    convert_text_to_html(cr)
