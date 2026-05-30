from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BeautyAppointment(models.Model):
    _name = 'beauty.appointment'
    _description = 'Beauty Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_time desc'

    name = fields.Char(string='Mã lịch hẹn', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    
    customer_id = fields.Many2one('res.partner', string='Khách hàng', required=True, tracking=True)
    room_id = fields.Many2one('beauty.room', string='Phòng điều trị', required=True, tracking=True)
    
    appointment_type = fields.Selection([
        ('consultation', 'Tư vấn'),
        ('treatment', 'Điều trị')
    ], string='Loại lịch hẹn', required=True, default='consultation', tracking=True)
    
    # Domains defined matching your hr.employee extensions in core
    doctor_id = fields.Many2one('hr.employee', string='Bác sĩ', domain=[('role_type', '=', 'doctor')], tracking=True)
    ktv_id = fields.Many2one('hr.employee', string='Kỹ thuật viên (KTV)', domain=[('role_type', '=', 'ktv')], tracking=True)
    
    start_time = fields.Datetime(string='Thời gian bắt đầu', required=True, tracking=True)
    end_time = fields.Datetime(string='Thời gian kết thúc', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('arrived', 'Đã đến'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('no_show', 'Vắng mặt'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi chú')
    category_id = fields.Many2one('product.category', string='Nhóm dịch vụ (Tag)', tracking=True)
    service_id = fields.Many2one('product.product', string='Dịch vụ', domain="[('type', '=', 'service')]", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('beauty.appointment') or _('New')
        return super().create(vals_list)

    @api.constrains('start_time', 'end_time', 'doctor_id', 'ktv_id', 'room_id', 'customer_id')
    def _check_conflicts(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu.")

            # 0. Check Room Maintenance
            if record.room_id and record.room_id.status == 'maintenance':
                raise ValidationError(
                    f"Phòng '{record.room_id.name}' đang trong trạng thái Bảo trì, không thể đặt lịch. "
                    f"Vui lòng chọn phòng khác hoặc liên hệ quản lý."
                )

            # Base domain for overlapping time
            overlap_domain = [
                ('id', '!=', record.id),
                ('state', 'not in', ['draft', 'cancelled', 'no_show']),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ]

            # 1. Check Customer Overlap
            cust_domain = overlap_domain + [('customer_id', '=', record.customer_id.id)]
            if self.search_count(cust_domain) > 0:
                raise ValidationError("Khách hàng này đã có lịch hẹn khác trong khung giờ này.")

            # 2. Check Personnel Overlap
            if record.appointment_type == 'consultation' and record.doctor_id:
                doc_domain = overlap_domain + [('doctor_id', '=', record.doctor_id.id)]
                if self.search_count(doc_domain) > 0:
                    raise ValidationError(f"Bác sĩ {record.doctor_id.name} đã kẹt lịch trong khung giờ này.")
            
            elif record.appointment_type == 'treatment' and record.ktv_id:
                ktv_domain = overlap_domain + [('ktv_id', '=', record.ktv_id.id)]
                if self.search_count(ktv_domain) > 0:
                    raise ValidationError(f"KTV {record.ktv_id.name} đã kẹt lịch trong khung giờ này.")

            # 3. Check Room Capacity
            if record.room_id:
                room_domain = overlap_domain + [('room_id', '=', record.room_id.id)]
                overlapping_appointments = self.search_count(room_domain)
                if overlapping_appointments >= record.room_id.capacity:
                    raise ValidationError(f"Phòng {record.room_id.name} đã vượt quá sức chứa ({record.room_id.capacity} giường) trong khung giờ này.")

    # Action methods for buttons
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_arrive(self):
        self.write({'state': 'arrived'})

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_no_show(self):
        self.write({'state': 'no_show'})