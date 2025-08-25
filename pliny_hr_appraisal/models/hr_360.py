from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ThreeSixty(models.Model):
    _name = "hr.threesixty"
    _description = "Employee 360"

    name = fields.Char('Name',required=True)
    start_date = fields.Date(
        string="Start Date",
        help="Start of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations")
    end_date = fields.Date(
        string="End Date",
        help="End of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations. Also acts as deadline of submissions")
    deadline = fields.Date(string="Submission Deadline")
    description = fields.Char(translate=False)
    minimum_review = fields.Integer(string="Minimum Reviews",
    		help="The minimum number of colleagues an employee can evaluate",
    		default=0)
    recommended_review = fields.Integer(string="Recommended Reviews",
    		help="The maximum number of colleagues an employee can evaluate")
    allocation_ids = fields.One2many('hr.appraisal.plan.allocation', 'plan_id', string="Allocations")
    question_ids = fields.One2many('hr.appraisal.plan.question', 'plan_id', string="Questions")

