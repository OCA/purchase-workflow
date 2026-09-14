.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Purchase Free-Of-Payment shipping
=================================

This module allows to define a Free-Of-Payment (FOP) shipping on supplier.
FOP shipping is a min purchase order amount to got shipping free from supplier.
User can force confirm purchase order if he/she wishes.

Configuration
=============

To configure this module, you need to:
Define an amount of FOP shipping for suppliers

Usage
=====

#. Go to ...

.. image:: https://img.shields.io/badge/github-OCA%2Fpurchase--workflow-lightgray.png?logo=github
    :target: https://github.com/OCA/purchase-workflow/tree/19.0/purchase_fop_shipping
    :alt: OCA/purchase-workflow

.. image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/purchase-workflow&target_branch=19.0
    :alt: Try me on Runboat

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* By upgrading the module you could have to re-configure all your FOP minimum amount on suppliers
  as this information is now company-related.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com.br>
* Dhara Solanki <dhara.solanki@initos.com>

Funders
-------

The development of this module has been financially supported by:

* Asler Diffusion

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
