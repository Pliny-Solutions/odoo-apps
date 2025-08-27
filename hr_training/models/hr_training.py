from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Training(models.Model):
    _name = "hr.training"
    _description = "Employee Training and Development Programs"

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    objective = fields.Char('Objective', help="What's the main objective of this training")
    target = fields.Char('Target Group', help="Describe the people who are expected to benefit from this training")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    persons_trained = fields.Integer(string="Trainees No", compute='_compute_persons_trained', required=True)
    trainee_ids = fields.One2many('hr.training.trainee', 'training_id', string="Trainees")
    attachment_ids = fields.One2many('hr.training.attachment', 'training_id', string="Attachments")


    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Supervising",
        required=True
    )

    department_id = fields.Many2one(
        'hr.department',
        string="Department"
    )

    training_type = fields.Selection([
        ('Internal', 'Internal'),
        ('External', 'External'),
        ('Other', 'Other'),
    ], string="Training Type", default='Internal', tracking=True)

    trainer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Training Partner',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    state = fields.Selection([
        ('planned', 'Planned'),
        ('approved', 'Approved'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed')
    ], string="Status", default='planned', tracking=True)


    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            self.end_date = self.start_date

    @api.constrains('start_date', 'end_date')
    def _check_end_date_after_start(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("End date must be after the start date.")

    @api.onchange('state')
    def _onchange_state(self):
        if self.state in ['cancelled', 'closed']:
            raise UserError("This record is not editable in this state.")

    def action_approve(self):
        self._check_state_modifiable()
        self.write({'state': 'approved'})


    def action_complete(self):
        self._check_state_modifiable()
        self.write({'state': 'done'})

    def action_cancel(self):
        self._check_state_modifiable()
        self.write({'state': 'cancelled'})

    def action_close(self):
        self._check_state_modifiable()
        self.write({'state': 'closed'})

    def _check_state_modifiable(self):
        for rec in self:
            if rec.state in ['cancelled', 'closed']:
                raise UserError("You cannot perform this action on a cancelled or closed training.")

    def unlink(self):
        for rec in self:
            if rec.state in ['cancelled', 'closed']:
                raise UserError("You cannot delete a training that is cancelled or closed.")
        return super().unlink()

    @api.depends('trainee_ids')
    def _compute_persons_trained(self):
        for rec in self:
            rec.persons_trained = len(rec.trainee_ids)


class TrainingTrainee(models.Model):
    _name = "hr.training.trainee"
    _description = "List of trainees who attended a training"

    training_id = fields.Many2one('hr.training', string="Training")

    employee_id = fields.Many2one(
        'hr.employee',
        string="Trainee",
        required=True
    )


    notes = fields.Char(string="Notes")

class HrTrainingAttachment(models.Model):
    _name = 'hr.training.attachment'
    _description = 'Training Attachments'

    name = fields.Char(string='Attachment Name', required=True)
    training_id = fields.Many2one('hr.training', string='Training', required=True, ondelete='cascade')
    attachment = fields.Binary(string='File', required=True)
    attachment_type = fields.Selection(
        selection=[
            ('training_material', 'Training Material'),
            ('receipt', 'Receipt'),
            ('invoice', 'Invoice'),
            ('general', 'General')
        ],
        string='Attachment Type',
        required=True
    )
