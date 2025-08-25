from odoo import models, fields

class Appraisal(models.Model):
    _name = "hr.appraisal"
    _description = "This is the appraisal for an employee"

    name = fields.Char('Description')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    appraisal_plan_id = fields.Many2one('hr.appraisal.plan', string="Appraisal Name", required=True)
    department_id = fields.Many2one('hr.department', string="Department")
    manager_id = fields.Many2one('hr.employee', string="Manager", required=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=False)
    employee_date = fields.Date(string="Employee Fill Date")
    manager_date = fields.Date(string="Manager Fill Date")
    deadline = fields.Date(string="Deadline")
    period = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('yearly', 'Yearly'),
    ], string="Evaluation Period", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved')
    ], default='draft', string='State')
    total_score = fields.Float(
        string="Average Score", compute='_compute_performance_score', store=True, group_operator="avg"
    )

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
