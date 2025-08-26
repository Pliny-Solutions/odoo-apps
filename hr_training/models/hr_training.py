from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Training(models.Model):
    _name = "hr.training"
    _description = "Employee and Entrepreneur Training"

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    objective = fields.Char('Objective', help="What's the main objective of this training")
    target = fields.Char('Target Group', help="Describe the people who are expected to benefit from this training")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    persons_trained = fields.Integer(string="Trainees No", compute='_compute_persons_trained', required=True)
    trainee_ids = fields.One2many('hr.training.trainee', 'training_id', string="Trainees")
    expense_ids = fields.One2many('hr.training.expense', 'training_id', string="Expenses")
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

    budget = fields.Monetary(
        string="Budget",
        currency_field='currency_id',
        help="Budget allocation for this training"
    )
    amount_spent = fields.Monetary(
        string="Amount Spent",
        currency_field='currency_id',
        compute='_compute_totals',
        readonly=True,
        help="Shows amount spent so far"
    )

    funder_id = fields.Many2one(
        comodel_name='res.partner',
        string='Funder',
        domain=[('is_funder', '=', True)],
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )

    total_reimbursement = fields.Monetary(
        string="Total Reimbursement",
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    total_expense = fields.Monetary(
        string="Total Expenses",
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    state = fields.Selection([
        ('planned', 'Planned'),
        ('approved', 'Approved'),
        ('ongoing', 'On Going'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed')
    ], string="Status", default='planned', tracking=True)

    @api.depends('trainee_ids.reimbursement', 'expense_ids.expense')
    def _compute_totals(self):
        for rec in self:
            rec.total_reimbursement = sum(t.reimbursement for t in rec.trainee_ids)
            rec.total_expense = sum(e.expense for e in rec.expense_ids)
            rec.amount_spent = rec.total_reimbursement + rec.total_expense

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

    def action_start(self):
        self._check_state_modifiable()
        self.write({'state': 'ongoing'})

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
    reimbursement = fields.Monetary(
        string="Reimbursement",
        currency_field='currency_id',
        default=0,
        help="Amount allocated to trainee as payment or reimbursement"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    notes = fields.Char(string="Notes")

class TrainingExpense(models.Model):
    _name = "hr.training.expense"
    _description = "Expenses incurred during training"

    training_id = fields.Many2one('hr.training', string="Training")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        help="Employee responsible for the expense"
    )
    name = fields.Char(string="Name", required=True)
    notes = fields.Char(string="Notes")
    expense = fields.Monetary(
        string="Expense",
        currency_field='currency_id',
        default=0,
        help="Cost of the expense item"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )


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
