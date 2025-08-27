from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    training_trainee_ids = fields.One2many(
        'hr.training.trainee',
        'employee_id',  # You'll need this field in hr.training.trainee
        string='Trainings Attended'
    )

    training_count = fields.Integer(
        string='Trainings',
        compute='_compute_training_count'
    )

    def _compute_training_count(self):
        for employee in self:
            employee.training_count = self.env['hr.training.trainee'].search_count([
                ('employee_id', '=', employee.id)
            ])

    def action_view_trainings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Trainings',
            'res_model': 'hr.training.trainee',
            'view_mode': 'kanban,tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
