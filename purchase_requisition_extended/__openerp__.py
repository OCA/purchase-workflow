# -*- coding: utf-8 -*-
{"name": "IFRC Purchase Requisition",
 "version": "0.1",
 "author": "Camp2Camp",
 "category": "Purchase Management",
 "complexity": "normal",
 "images": [],
 "description": """
This module improves the Purchase Requisition.
==============================================

IFRC specific.

""",
 "depends": ["purchase_requisition",
             "stock",  # For incoterm
             "purchase_extended", #for fields incoterm adress
             ],
 "demo": [],
 "data": ["view/purchase_requisition.xml",
          "view/purchase_order.xml",
          "workflow/purchase_order.xml"],
 "auto_install": False,
 "test": [],
 "installable": True,
 "certificate": "",
 }
