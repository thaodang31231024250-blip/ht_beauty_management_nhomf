from odoo import models, fields, api

class BeautyTreatmentSession(models.Model):
    _name = 'beauty.treatment.session'
    _description = 'Nhật ký buổi điều trị'
    _inherit = ['mail.thread']

    name = fields.Char(string='Tên buổi', required=True, placeholder="Ví dụ: Buổi 1 - Laser")
    plan_id = fields.Many2one('beauty.treatment.plan', string='Phác đồ', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='plan_id.partner_id', string='Khách hàng', store=True)
    
    appointment_id = fields.Many2one('beauty.appointment', string='Lịch hẹn liên kết')
    date = fields.Date(string='Ngày thực hiện', default=fields.Date.context_today)
    
    ktv_id = fields.Many2one('hr.employee', string='KTV thực hiện', domain="[('role_type', '=', 'ktv')]")
    
    before_image = fields.Image(string='Ảnh trước điều trị', max_width=1024, max_height=1024)
    after_image = fields.Image(string='Ảnh sau điều trị', max_width=1024, max_height=1024)
    
    clinical_notes = fields.Text(string='Nhật ký / Ghi chú lâm sàng')
    
    state = fields.Selection([
        ('draft', 'Lên kế hoạch'),
        ('done', 'Đã thực hiện'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', tracking=True)

    def action_mark_done(self):
        self.write({'state': 'done'})