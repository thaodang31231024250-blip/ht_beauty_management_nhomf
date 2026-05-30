# -*- coding: utf-8 -*-

from odoo import models, fields

class BeautyRoom(models.Model):
    _name = 'beauty.room'
    _description = 'Phòng điều trị'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên phòng', required=True, tracking=True)
    code = fields.Char(string='Mã phòng', required=True)
    active = fields.Boolean(string='Hoạt động', default=True)
    status = fields.Selection([
        ('available', 'Sẵn sàng'),
        ('maintenance', 'Bảo trì')
    ], string='Trạng thái', default='available', tracking=True, required=True)
    
    capacity = fields.Integer(string='Số giường', default=1)
    notes = fields.Text(string='Ghi chú nội bộ')