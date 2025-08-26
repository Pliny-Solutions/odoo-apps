{
    'name': 'HR Training',
    'version': '17.0',
    'category': 'Human Resources',
    'author': 'Pliny Solutions',
    'website': 'https://plinysolutions.com/odoo',
    'sequence': 92,
    'license': 'LGPL-3',
    'images': ['static/description/cover.png'],
    'summary': 'Keep track of all trainings done to employees and partners',

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
    'description': "List of all trainings that are done by the company to both employees and other partners",
    'installable': True,
    'application': True
}
