from odoo import models, fields

class AppraisalScore(models.Model):
    _name = "hr.appraisal.score"
    _description = "Create a scoring system"

    name = fields.Char('Name',required=True)
    description = fields.Text(translate=True)
    minimum_value = fields.Integer(string="Minimum Value", required=True, default=0)
    maximum_value = fields.Integer(string="Maximum Value", required=True)

    _sql_constraints = [
        ('minimum_value', 'CHECK(minimum_value >= 0)','The minimum value must be a positive value or 0.'),
        ('maximum_value', 'CHECK(maximum_value > minimum_value)', 'The maximum value must be great than the minimum value.')
    ]
