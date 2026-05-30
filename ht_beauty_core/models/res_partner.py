# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # =========================
    # 1. THÔNG TIN CƠ BẢN & LIÊN HỆ
    # =========================
    birthday = fields.Date(string='Ngày sinh')
    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string='Giới tính')
    zalo_link = fields.Char(string='Link Zalo')
    customer_source = fields.Selection([
        ('facebook', 'Facebook'),
        ('zalo', 'Zalo'),
        ('walk_in', 'Khách vãng lai'),
        ('referral', 'Người quen giới thiệu'),
        ('other', 'Khác')
    ], string='Nguồn khách hàng', default='facebook')

    # =========================
    # 2. THÔNG TIN Y TẾ
    # =========================
    medical_history = fields.Text(string='Tiền sử bệnh lý')
    allergy_note = fields.Text(string='Thông tin dị ứng')
    chronic_disease = fields.Selection([
        ('none', 'Không'),
        ('diabetes', 'Tiểu đường'),
        ('hypertension', 'Huyết áp cao'),
        ('heart', 'Tim mạch'),
        ('other', 'Khác')
    ], string='Bệnh nền', default='none')
    using_medicine = fields.Boolean(string='Đang sử dụng thuốc')
    medicine_note = fields.Text(string='Chi tiết thuốc đang dùng')

    # =========================
    # 3. ĐẶC ĐIỂM THẨM MỸ
    # =========================
    skin_type = fields.Selection([
        ('dry', 'Da khô'),
        ('oily', 'Da dầu'),
        ('combination', 'Da hỗn hợp'),
        ('sensitive', 'Da nhạy cảm')
    ], string='Loại da')
    skin_condition = fields.Selection([
        ('acne', 'Mụn'),
        ('melasma', 'Nám'),
        ('freckles', 'Tàn nhang'),
        ('scar', 'Sẹo'),
        ('aging', 'Lão hóa')
    ], string='Tình trạng da')
    treatment_goal = fields.Text(string='Nhu cầu điều trị')

    skin_analysis_image = fields.Image(string='Ảnh soi da', max_width=1024, max_height=1024)
    skin_analysis_notes = fields.Html(string='Mô tả tình trạng da')

    # =========================
    # 4. THÔNG TIN ĐIỀU TRỊ
    # =========================
    treatment_status = fields.Selection([
        ('new', 'Mới'),
        ('consulted', 'Đã tư vấn'),
        ('in_progress', 'Đang điều trị'),
        ('completed', 'Hoàn thành')
    ], string='Trạng thái điều trị', default='new')
    session_count = fields.Integer(string='Số buổi điều trị')
    next_appointment = fields.Date(string='Lịch hẹn tiếp theo')
    treatment_note = fields.Text(string='Ghi chú điều trị')

    # =========================
    # 5. KIỂM TRA TRÙNG SĐT
    # =========================
    @api.constrains('phone')
    def _check_duplicate_phone(self):
        for record in self:
            phones = []
            if record.phone:
                phones.append(record.phone)
            
            has_mobile = 'mobile' in record._fields
            if has_mobile and record.mobile:
                phones.append(record.mobile)

            if not phones:
                continue

            domain = [('id', '!=', record.id)]
            
            if has_mobile:
                domain += ['|', ('phone', 'in', phones), ('mobile', 'in', phones)]
            else:
                domain += [('phone', 'in', phones)]

            duplicate = self.search(domain, limit=1)

            if duplicate:
                raise ValidationError(
                    "Số điện thoại (%s) đã tồn tại trong hệ thống thuộc về khách hàng: %s. Vui lòng kiểm tra lại!"
                    % (', '.join(phones), duplicate.name)
                )