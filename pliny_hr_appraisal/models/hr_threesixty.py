from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ThreeSixty(models.Model):
    _name = "hr.threesixty.review"
    _description = "Employee 360"

    #Name should be a many to One
    plan_id = fields.Many2one('hr.threesixty.plan', string="360 Plan")
    allocation_id = fields.Many2one('hr.threesixty.plan.allocation', string="Reviewer List")
    review_list_id = fields.Many2one('hr.threesixty.review.list', string="Reviewed List")
    reviewer_id = fields.Many2one('hr.employee', string="Reviewer", required=True, readonly = True, related='allocation_id.reviewer_id', store=True)
    reviewed_id = fields.Many2one('hr.employee', string="Reviewed", required=True, readonly = True, related='review_list_id.reviewed_id', store=True)
    submit_date = fields.Date(string="Submit Date", readonly=True)
    department_id = fields.Many2one('hr.department', string="Department")
    manager_id = fields.Many2one('hr.employee', string="Manager")
    job_id = fields.Many2one('hr.job', string="Job Title")
    #total_score = fields.Integer(string="Total Score", compute="_compute_score", store=True)
    question_review_ids = fields.One2many('hr.threesixty.review.question', 'review_id', string="Questions")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)

    @api.onchange('reviewed_id')
    def _onchange_reviewed_id(self):
        if self.reviewed_id:
            self.job_id = self.reviewed_id.job_id
            self.manager_id = self.reviewed_id.parent_id
            self.department_id = self.reviewed_id.department_id
        else:
            self.department_id = False
            self.job_id = False
            self.manager_id= False

    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft reviews can be submitted."))
            record.state = 'done'
            record.submit_date = fields.Date.today()

            # Also mark the parent review_list_id as done
            if record.review_list_id:
                record.review_list_id.state = 'done'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

class ThreeSixtyPlanReviewList(models.Model):
    _name = "hr.threesixty.review.list"
    _description = "List of employees who are being assessed"


    plan_id = fields.Many2one('hr.threesixty.plan', related="allocation_id.plan_id", string="360 Plan")
    allocation_id = fields.Many2one('hr.threesixty.plan.allocation', string="Allocation List")
    state = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('done', 'Done'),
    ], string="Status", default='new')
    reviewer_id = fields.Many2one('hr.employee', string="Reviewer",  related='allocation_id.reviewer_id', store=True)
    reviewed_id = fields.Many2one('hr.employee', string="To be Reviewed")
    review_ids = fields.One2many('hr.threesixty.review', 'review_list_id', string="Reviews List")

    def action_generate_review(self):
        self.ensure_one()

        self.state = "active"

        # Check if a review already exists
        existing_review = self.env['hr.threesixty.review'].search([
            ('review_list_id', '=', self.id),
            ('reviewer_id', '=', self.reviewer_id.id),
            ('reviewed_id', '=', self.reviewed_id.id),
            ('plan_id', '=', self.plan_id.id)
        ], limit=1)

        if not existing_review:
            review = self.env['hr.threesixty.review'].create({
                'plan_id': self.plan_id.id,
                'allocation_id': self.allocation_id.id,
                'review_list_id': self.id,
                'reviewer_id': self.reviewer_id.id,
                'reviewed_id': self.reviewed_id.id,
                'department_id': self.reviewed_id.department_id.id,
                'job_id': self.reviewed_id.job_id.id,
                'manager_id': self.reviewed_id.parent_id.id,
            })
        # Clone questions from plan to the review
            question_vals = []
            for question in self.plan_id.question_ids:
                question_vals.append({
                    'plan_id': self.plan_id.id,
                    'review_id': review.id,
                    'name': question.name,
                    'description': question.description,
                    'maximum_value': question.maximum_value,
                })
            self.env['hr.threesixty.review.question'].create(question_vals)


        else:
            review = existing_review

        return {
            'type': 'ir.actions.act_window',
            'name': 'Review',
            'res_model': 'hr.threesixty.review',
            'res_id': review.id,
            'view_mode': 'form',
            'target': 'current',
        }


    def action_open_review(self):
        self.ensure_one()
        review = self.env['hr.threesixty.review'].search([
            ('review_list_id', '=', self.id),
        ], limit=1)

        if not review:
            raise UserError("No review found for this line.")

        return {
            'type': 'ir.actions.act_window',
            'name': '360 Review',
            'res_model': 'hr.threesixty.review',
            'view_mode': 'form',
            'res_id': review.id,
            'target': 'current',
        }


    #Prevent deletion of records that have been allocated
    def unlink(self):
            for record in self:
                if record.state == 'done':
                    raise UserError("You cannot delete a record that is already done.")
            return super().unlink()


class ThreeSixtyReviewQuestion(models.Model):
    _name = "hr.threesixty.review.question"
    _description = "List of questions every employee under this plan must be asked"


    plan_id = fields.Many2one('hr.threesixty.plan', string="360 Plan")
    review_id = fields.Many2one('hr.threesixty.review', string="360 Review")
    name = fields.Char(string="Question Title", required=True)
    description = fields.Char(string="Description")
    maximum_value = fields.Integer(string="Maximum Value")
    reviewer_value = fields.Integer(string="Reviewer Score", default=0)
    reviewer_comment = fields.Char(string="Reviewer Comments")

    #Not proud but I need to work with this
    #appraisal_state = fields.Selection(related='appraisal_id.state',store=True,string='Appraisal State')

    _sql_constraints = [
        ('reviewer_value', 'CHECK(reviewer_value >= 0)','The employee value must be a positive value or 0.'),
        ('reviewer_value', 'CHECK(maximum_value >= reviewer_value)', 'The employee score cant exceed the maximum.')
    ]
