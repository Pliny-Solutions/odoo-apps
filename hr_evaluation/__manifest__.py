{
    'name': 'HR Evaluation',
    'version': '17.0',
    'category': 'Human Resources',
    'author': 'Pliny Solutions',
    'website': 'https://plinysolutions.com',
    'sequence': 90,
    'license': 'LGPL-3',
    'images': ['static/description/cover.png'],
    'summary': 'Manage employee performance evaluations using KPIs.',

    'depends': [
    		'hr',
    		'base',
    		],
     'data': [
        'security/appraisal_groups.xml',
        'security/ir.model.access.csv',
        'security/appraisal_record_rules.xml',
        'data/mail_template.xml',
        'data/appraisal_score.xml',
        'data/appraisal_category.xml',
        'views/add_employees.xml',
        'views/hr_appraisal.xml',
        'views/hr_threesixty_plan.xml',
        'views/hr_threesixty.xml',
        'views/hr_appraisal_plan.xml',
        'views/hr_appraisal_views.xml',
    ],
    'description': " HR Appraisals, KPI's and 360 degree feedback",
    'installable': True,
    'application': True
}
