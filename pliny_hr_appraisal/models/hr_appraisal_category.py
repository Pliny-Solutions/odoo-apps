from odoo import models, fields

class AppraisalCategory(models.Model):
    _name = "hr.appraisal.category"
    _description = "List of the categories the appraisal questions can fall into"

    name = fields.Char('Name',required=True)
    description = fields.Text(translate=True)


