from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Appraisal(models.Model):
    _name = "hr.appraisal"
    _description = "Employee Appraisal"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    manager_id = fields.Many2one('hr.employee', string="Manager")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Job Title")
    plan_id = fields.Many2one('hr.appraisal.plan', string="Appraisal Plan")
    category_id = fields.Many2one('hr.appraisal.category', string="Category")
    start_date = fields.Date()
    end_date = fields.Date()
    deadline = fields.Date()
    question_ids = fields.One2many('hr.appraisal.question', 'appraisal_id', string="Questions")
    total_employee_score = fields.Integer(string="Total Employee Score", compute="_compute_employee_score", store=True)
    employee_score_percentage = fields.Float(string="Employee Score (%)", compute="_compute_employee_score", store=True)
    total_manager_score = fields.Integer(string="Total Manager Score", compute="_compute_manager_score", store=True)
    manager_score_percentage = fields.Float(string="Manager Score (%)", compute="_compute_manager_score", store=True)
    employee_submit_date = fields.Date()
    manager_submit_date = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_review', 'Manager Review'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', tracking=True)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.manager_id = self.employee_id.parent_id
            self.department_id = self.employee_id.department_id
        else:
            self.manager_id = False
            self.department_id = False
            self.job_id = False

    @api.onchange('employee_id')
    def _onchange_employee_company(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id

    def action_draft(self):
        for record in self:
            record.state = "draft"
        return True

    def action_submit(self):
        for record in self:
            record.state = "submitted"
        return True

    def action_submit(self):
        self.state = 'submitted'
        self.employee_submit_date = fields.Date.today()

    def action_manager_review(self):
        self.state = 'manager_review'
        self.manager_submit_date = fields.Date.today()

    def action_complete(self):
        self.state = 'done'

    @api.depends('question_ids.employee_value', 'question_ids.maximum_value')
    def _compute_employee_score(self):
        for record in self:
            total_score = sum(q.employee_value for q in record.question_ids)
            max_score = sum(q.maximum_value for q in record.question_ids)
            record.total_employee_score = total_score
            record.employee_score_percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

    @api.depends('question_ids.employee_value', 'question_ids.maximum_value')
    def _compute_manager_score(self):
        for record in self:
            total_score = sum(q.manager_value for q in record.question_ids)
            max_score = sum(q.maximum_value for q in record.question_ids)
            record.total_manager_score = total_score
            record.manager_score_percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

    #Prevent deletion of records that have been allocated
    def unlink(self):
            for record in self:
                if record.state == 'done':
                    raise UserError("You cannot delete a record that is already done.")
            return super().unlink()



class AppraisalQuestion(models.Model):
    _name = "hr.appraisal.question"
    _description = "This is the appraisal for an employee"

    appraisal_id = fields.Many2one('hr.appraisal', string="Appraisal")
    name = fields.Char(string="Question Title", required=True)
    description = fields.Char(string="Description")
    maximum_value = fields.Integer(string="Maximum Value")
    employee_value = fields.Integer(string="Employee Score", default=0)
    employee_comment = fields.Char(string="Employee Comments")
    manager_value = fields.Integer(string="Manager Score", default=0)
    manager_comment = fields.Char(string="Manager Comments")

    #Not proud but I need to work with this
    appraisal_state = fields.Selection(
        related='appraisal_id.state',
        store=True,
        string='Appraisal State'
    )

    _sql_constraints = [
        ('manager_value', 'CHECK(manager_value >= 0 and maximum_value >= manager_value )','The manager value  cant be greater than the maximum and not lower than the minimum.'),
        ('employee_value', 'CHECK(employee_value >= 0)','The employee value must be a positive value or 0.'),
        ('employee_value', 'CHECK(maximum_value >= employee_value)', 'The employee score cant exceed the maximum.')
    ]


