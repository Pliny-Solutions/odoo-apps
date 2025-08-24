from odoo import models, fields, api

class RoomProperty(models.Model):
    _name = 'room.property'
    _description = 'Property'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    location_ids = fields.Many2one('hr.work_location', string='Work Locations')
    number_of_rooms = fields.Integer(string='Number of Rooms')
    property_type = fields.Selection(
        [('rented', 'Rented'),
        ('owned', 'Owned')],
        string='Type of Property',
        required=True
    )
    room_ids = fields.One2many('room.property.room', 'property_id',string='Rooms')

class PropertyRoom(models.Model):
    _name = 'room.property.room'
    _description = 'Room within Property'

    name = fields.Char(string='Room Name', required=True)
    room_type = fields.Selection(
        [
            ('single', 'Single'),
            ('double', 'Double'),
            ('suite', 'Suite'),
            ('conference', 'Conference'),
        ],
        string='Room Type',
        required=True
    )
    property_id = fields.Many2one('room.property', string='Property', required=True)
    property_name = fields.Char(related='property_id.name', string='Property Name', store=True)

    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.property_id.name})") for rec in self]

