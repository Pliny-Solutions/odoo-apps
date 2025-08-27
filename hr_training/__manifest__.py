{
    'name': 'HR Training and Development Programs',
    'version': '17.0',
    'category': 'Human Resources',
    'author': 'Pliny Solutions',
    'website': 'https://plinysolutions.com/odoo',
    'sequence': 92,
    'license': 'LGPL-3',
    'images': ['static/description/cover.png'],
    'summary': 'Employee Training and Development Programs',

    'depends': [
    		'hr',
    		'base',
    		],
        'data': [
        'views/hr_training.xml',
        'views/hr_employee_views.xml',
        'security/training_groups.xml',
        'security/training_record_rules.xml',
        'security/ir.model.access.csv',
    ],
    'description': "List of all Employee Training and Development Programs offered by the Company whether internally or using external partners",
    'installable': True,
    'application': True
}
