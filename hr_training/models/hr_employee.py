from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    training_trainee_ids = fields.One2many(
        'hr.training.trainee',
        'employee_id',  # You'll need this field in hr.training.trainee
        string='Trainings Attended'
    )

    training_count = fields.Integer(
        string='Trainings Attended',
        compute='_compute_training_count'
    )

    def _compute_training_count(self):
        for employee in self:
            employee.training_count = self.env['hr.training.trainee'].search_count([
                ('employee_id', '=', employee.id)
            ])


