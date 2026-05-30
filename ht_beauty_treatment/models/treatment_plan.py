from odoo import models, fields, api, _

# Model phụ: Chi tiết dịch vụ trong phác đồ (Giống hệt Sale Order Line)
class BeautyTreatmentPlanLine(models.Model):
    _name = 'beauty.treatment.plan.line'
    _description = 'Chi tiết dịch vụ phác đồ'

    plan_id = fields.Many2one('beauty.treatment.plan', string='Phác đồ', index=True, ondelete='cascade')
    
    # 3 field cốt lõi để tạo ra "Thêm phần" và "Thêm ghi chú"
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
    name = fields.Text(string='Mô tả', required=True)
    
    # Các field tính tiền và sản phẩm
    product_id = fields.Many2one('product.product', string='Dịch vụ/Sản phẩm', domain="[('type', '=', 'service')]")
    quantity = fields.Float(string='Số lượng', default=1.0)
    price_unit = fields.Float(string='Đơn giá')
    price_subtotal = fields.Float(string='Số tiền', compute='_compute_subtotal', store=True)


    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            
    # Tự động lấy tên và giá khi chọn dịch vụ
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price

# Model Thẻ (Tags)
class BeautyTreatmentTag(models.Model):
    _name = 'beauty.treatment.tag'
    _description = 'Thẻ phân loại phác đồ'

    name = fields.Char(string='Tên Tag', required=True)
    color = fields.Integer(string='Màu sắc')

# Model chính: Phác đồ
class BeautyTreatmentPlan(models.Model):
    _name = 'beauty.treatment.plan'
    _description = 'Phác đồ điều trị'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Mã Phác Đồ', required=True, copy=False, readonly=True, default=lambda self: _('Mới'))
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True, tracking=True)
    doctor_id = fields.Many2one('hr.employee', string='Bác sĩ phụ trách', domain="[('role_type', '=', 'doctor')]", tracking=True)
    
    category_id = fields.Many2one('product.category', string='Phân loại điều trị (Tag)', tracking=True)
    tag_ids = fields.Many2many('beauty.treatment.tag', string='Phân loại (Tags)')
    
    # --- ĐÃ SỬA: Thay thế Many2many bằng One2many nối sang model Line ---
    line_ids = fields.One2many('beauty.treatment.plan.line', 'plan_id', string='Chi tiết phác đồ')
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Đang điều trị'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', tracking=True)

    session_ids = fields.One2many('beauty.treatment.session', 'plan_id', string='Nhật ký các buổi')

    # --- MỚI: Smart button đếm nhật ký ---
    session_count = fields.Integer(string='Số buổi', compute='_compute_session_count')

    @api.depends('session_ids')
    def _compute_session_count(self):
        for plan in self:
            plan.session_count = len(plan.session_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Mới')) == _('Mới'):
                vals['name'] = self.env['ir.sequence'].next_by_code('beauty.treatment.plan') or _('Phác đồ mới')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'active'})

    def action_done(self):
        self.write({'state': 'completed'})

    # --- MỚI: Mở danh sách nhật ký điều trị ---
    def action_view_sessions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhật ký điều trị',
            'res_model': 'beauty.treatment.session',
            'view_mode': 'list,form',
            'domain': [('plan_id', '=', self.id)],
            'context': {'default_plan_id': self.id, 'default_partner_id': self.partner_id.id},
        }

    # --- MỚI: Mở Wizard tạo lịch hẹn hàng loạt ---
    def action_open_bulk_appointment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Xếp lịch hàng loạt',
            'res_model': 'beauty.bulk.appointment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_plan_id': self.id},
        }