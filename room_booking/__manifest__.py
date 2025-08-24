# Part of Odoo. See LICENSE file for full copyright and licensing details.

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Room Booking',
    'version': '1.0',
    'category': 'Human Resources/Room Booking',
    'sequence': 23,
    'summary': 'Allow employees to book stays at company houses',
    'description': "",
    'website': 'https://erp.somoafrica.org/',
    'depends': [
        'base_setup',
    ],
    'data': [
        'security/room_groups.xml',
        'security/ir.model.access.csv',
        'views/property.xml',
        'views/booking.xml',
        'views/room_booking_menu.xml',

     ],
    'demo': [
     ],
    'css': [
     ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False
}
