from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ThreeSixtyPlan(models.Model):
    _name = "hr.threesixty.plan"
    _description = "Employee 360"

    name = fields.Char('Name',required=True)
    start_date = fields.Date(
        string="Start Date",
        help="Start of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations")
    end_date = fields.Date(
        string="End Date",
        help="End of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations. Also acts as deadline of submissions")
    deadline = fields.Date(string="Submission Deadline")
    description = fields.Char(translate=False, string = "Instructions")
    score_id = fields.Many2one('hr.appraisal.score', string="Scoring System")
    minimum_review = fields.Integer(string="Minimum Reviews",
        help="The minimum number of colleagues an employee can evaluate",
        default=0)
    recommended_review = fields.Integer(string="Recommended Reviews",
        help="The maximum number of colleagues an employee can evaluate")
    allocation_ids = fields.One2many('hr.threesixty.plan.allocation', 'plan_id', string="Allocations")
    reviewed_ids = fields.One2many('hr.threesixty.review.list', 'plan_id', string="Reviewed")
    review_ids = fields.One2many('hr.threesixty.review', 'plan_id', string="Reviews")
    question_ids = fields.One2many('hr.threesixty.plan.question', 'plan_id', string="Questions List")
    question_review_ids = fields.One2many('hr.threesixty.review.question', 'plan_id', string="Review Questions")

    def open_add_employees_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.threesixty.add.employees.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_plan_id': self.id,
            }
        }


class ThreeSixtyPlanAllocation(models.Model):
    _name = "hr.threesixty.plan.allocation"
    _description = "List of employees who should fill out this 360 plan Essential for email"


    plan_id = fields.Many2one('hr.threesixty.plan', string="360 Plan")
    reviewer_id = fields.Many2one('hr.employee', string="Reviewer", required=True)
    number_of_reviews = fields.Integer(string="Number of Reviews",  compute="_compute_review_count", readonly = True)
    review_list_ids = fields.One2many('hr.threesixty.review.list', 'allocation_id', string="Reviews List")
    review_ids = fields.One2many('hr.threesixty.review', 'allocation_id', string="Reviews")

    @api.depends('reviewer_id')
    def _compute_review_count(self):
        for rec in self:
            rec.number_of_reviews = self.env['hr.threesixty.review'].search_count([
                ('reviewer_id', '=', rec.reviewer_id.id),
                ('plan_id', '=', rec.plan_id.id),
            ])

class ThreeSixtyPlanQuestion(models.Model):
    _name = "hr.threesixty.plan.question"
    _description = "List of questions every employee under this plan must be asked"


    plan_id = fields.Many2one('hr.threesixty.plan', string="360 Plan")
    name = fields.Char(string="Question", required=True)
    description = fields.Char(string="Description")
    score_id = fields.Many2one('hr.appraisal.score', related="plan_id.score_id", string="Scoring System", readonly=True)
    maximum_value = fields.Integer(string="Maximum Score", compute="_compute_maximum_value", store=True)


    @api.depends('plan_id.score_id.maximum_value')
    def _compute_maximum_value(self):
        for question in self:
            question.maximum_value = question.plan_id.score_id.maximum_value or 0
