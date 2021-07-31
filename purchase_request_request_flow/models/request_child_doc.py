# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RequestChildDoc(models.Model):
    _inherit = "request.child.doc"

    def _update_doc_info(self):
        super()._update_doc_info()
        if self.res_model == "purchase.request":
            self.update(
                {
                    "doc_amount": self.doc_ref.estimated_cost,
                    "doc_note": self.doc_ref.description,
                    "doc_status": dict(self.doc_ref._fields["state"].selection).get(
                        self.doc_ref.state
                    ),
                }
            )

    def _get_sql(self):
        queries = super()._get_sql()
        queries.append(
            """
            select
                1000000 + pr.id as id,
                ref_request_id as request_id,
                pr.id as res_id,
                'purchase.request' as res_model,
                'purchase.request,' || pr.id as doc_ref
            from purchase_request pr
            where pr.ref_request_id is not null
        """
        )
        return queries
