# This file is part of an Adiczion's Module.
# The COPYRIGHT and LICENSE files at the top level of this repository
# contains the full copyright notices and license terms.
{
    'name': 'Module Website Delivery Relaypoint',
    'version': '15.0.3',
    'author': 'Adiczion SARL',
    'category': 'Adiczion',
    'license': 'AGPL-3',
    'depends': [
        'website_sale',
        'a4o_delivery_relaypoint',
    ],
    'demo': [],
    'website': 'http://adiczion.com',
    'description': """
Module Website Delivery Relaypoint
==================================

Add relay points management on the web frontend 

    """,
    'data': [
        # 'security/objects_security.xml',
        # 'security/ir.model.access.csv',
        # 'wizard/your_wizard_name.xml',
        # 'data/data_for_your_module.xml',
        'views/templates.xml',
    ],
    'assets':{
        'web.assets_frontend': [
            "/a4o_website_delivery_relaypoint/static/src/css/lib/leaflet/leaflet.css",
            "/a4o_website_delivery_relaypoint/static/src/css/lib/leaflet/customize_leaflet.css",
            "/a4o_website_delivery_relaypoint/static/src/js/lib/leaflet/leaflet.js",
            "/a4o_website_delivery_relaypoint/static/src/js/website_sale_delivery.js",
        ],
    },
    'images': ['static/description/banner.png'],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
