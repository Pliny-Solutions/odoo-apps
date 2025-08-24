from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Room Booking'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    manager_id = fields.Many2one('hr.employee', string='Manager')
    room_id = fields.Many2one('room.property.room', string='Room', required=True)
    property_id = fields.Many2one('room.property', string='Property', required=True)
    check_in = fields.Date(string='Check-in Date', required=True)
    check_out = fields.Date(string='Check-out Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('checked_out', 'Checked Out')
    ], default='draft', string='Status')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.manager_id = self.employee_id.parent_id
        else:
            self.manager_id = False

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_check_out(self):
        for rec in self:
            rec.state = 'checked_out'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'


    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id:
            return {
                'domain': {
                    'room_id': [('property_id', '=', self.property_id.id)]
                }
            }
        return {
            'domain': {
                'room_id': []
            }
        }

    @api.constrains('property_id', 'room_id')
    def _check_room_belongs_to_property(self):
        for rec in self:
            if rec.room_id and rec.property_id and rec.room_id.property_id != rec.property_id:
                raise ValidationError("The selected room does not belong to the selected property.")


    @api.constrains('room_id', 'check_in', 'check_out')
    def _check_double_booking(self):
        for record in self:
            if not record.room_id or not record.check_in or not record.check_out:
                continue

            overlapping = self.env['room.booking'].search([
                ('id', '!=', record.id),
                ('room_id', '=', record.room_id.id),
                ('check_in', '<', record.check_out),
                ('check_out', '>', record.check_in),
            ], limit=1)

            if overlapping:
                raise ValidationError(
                    f"The room '{record.room_id.name}' is already booked. Please select another room in the same property to check availability"
                    f"from {overlapping.check_in} to {overlapping.check_out}."
                )

    @api.constrains('check_in', 'check_out')
    def _check_date_order(self):
        for record in self:
            if record.check_in and record.check_out and record.check_out <= record.check_in:
                raise ValidationError("Check-out must be after check-in.")

    def unlink(self):
        for rec in self:
            if rec.state in ['confirmed', 'checked_out']:
                raise ValidationError("You cannot delete a booking that is confirmed or checked out.")
        return super(RoomBooking, self).unlink()
