from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrThreesixtyAddEmployeesWizard(models.TransientModel):
    _name = 'hr.threesixty.add.employees.wizard'
    _description = 'Add Employees to 360 Plan'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    plan_id = fields.Many2one('hr.threesixty.plan', string='Plan', required=True)

    def action_add_employees(self):
        for employee in self.employee_ids:
            exists = self.env['hr.threesixty.plan.allocation'].search([
                ('plan_id', '=', self.plan_id.id),
                ('reviewer_id', '=', employee.id)
            ], limit=1)
            if not exists:
                self.env['hr.threesixty.plan.allocation'].create({
                    'plan_id': self.plan_id.id,
                    'reviewer_id': employee.id
                })

class HrAppraisalAddEmployeesWizard(models.TransientModel):
    _name = 'hr.appraisal.add.employees.wizard'
    _description = 'Add Employees to Appraisal Plan'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    plan_id = fields.Many2one('hr.appraisal.plan', string='Plan', required=True)

    def action_add_appraisal_employees(self):
        for employee in self.employee_ids:
            exists = self.env['hr.appraisal.plan.allocation'].search([
                ('plan_id', '=', self.plan_id.id),
                ('employee_id', '=', employee.id)
            ], limit=1)
            if not exists:
                self.env['hr.appraisal.plan.allocation'].create({
                    'plan_id': self.plan_id.id,
                    'employee_id': employee.id
                })
