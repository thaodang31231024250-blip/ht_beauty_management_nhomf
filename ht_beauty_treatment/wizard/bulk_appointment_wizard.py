from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BeautyBulkAppointmentWizard(models.TransientModel):
    _name = 'beauty.bulk.appointment.wizard'
    _description = 'Tạo lịch hẹn hàng loạt từ Phác đồ'

    plan_id = fields.Many2one('beauty.treatment.plan', string='Phác đồ', required=True, readonly=True)
    partner_id = fields.Many2one(related='plan_id.partner_id', string='Khách hàng', readonly=True)
    line_ids = fields.One2many('beauty.bulk.appointment.wizard.line', 'wizard_id', string='Chi tiết buổi hẹn')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        plan_id = self.env.context.get('default_plan_id') or self.env.context.get('active_id')
        if plan_id:
            plan = self.env['beauty.treatment.plan'].browse(plan_id)
            lines = []
            session_num = 1
            for line in plan.line_ids:
                if line.display_type or not line.product_id:
                    continue
                # Sinh tự động các buổi tương ứng với số lượng dịch vụ
                for qty in range(int(line.quantity)):
                    lines.append((0, 0, {
                        'name': f'Buổi {session_num} - {line.product_id.name}',
                        'product_id': line.product_id.id,
                    }))
                    session_num += 1
            res['line_ids'] = lines
        return res

    def action_create_appointments(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError("Không có dịch vụ nào để xếp lịch.")

        appointments = self.env['beauty.appointment']
        for line in self.line_ids:
            if not line.start_time or not line.end_time or not line.room_id:
                raise ValidationError(
                    f"Buổi '{line.name}' chưa được điền đầy đủ thông tin (Thời gian bắt đầu, Kết thúc, Phòng). "
                    f"Vui lòng điền đầy đủ trước khi tạo."
                )

            # Tạo lịch hẹn
            appointment = self.env['beauty.appointment'].create({
                'customer_id': self.partner_id.id,
                'room_id': line.room_id.id,
                'appointment_type': 'treatment',
                'ktv_id': line.ktv_id.id if line.ktv_id else False,
                'doctor_id': line.doctor_id.id if line.doctor_id else False,
                'start_time': line.start_time,
                'end_time': line.end_time,
                'service_id': line.product_id.id if line.product_id else False,
                'state': 'confirmed',
            })

            # Tạo Nhật ký điều trị (Session) tương ứng liên kết lịch hẹn
            self.env['beauty.treatment.session'].create({
                'name': line.name,
                'plan_id': self.plan_id.id,
                'appointment_id': appointment.id,
                'date': line.start_time.date() if line.start_time else False,
                'ktv_id': line.ktv_id.id if line.ktv_id else False,
                'state': 'draft',
            })
            appointments |= appointment

        # Trả về danh sách lịch hẹn vừa tạo
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lịch hẹn đã tạo',
            'res_model': 'beauty.appointment',
            'view_mode': 'list,form,calendar',
            'domain': [('id', 'in', appointments.ids)],
            'target': 'current',
        }


class BeautyBulkAppointmentWizardLine(models.TransientModel):
    _name = 'beauty.bulk.appointment.wizard.line'
    _description = 'Dòng xếp lịch hàng loạt'

    wizard_id = fields.Many2one('beauty.bulk.appointment.wizard', string='Wizard', ondelete='cascade')
    name = fields.Char(string='Tên buổi', required=True)
    product_id = fields.Many2one('product.product', string='Dịch vụ')
    start_time = fields.Datetime(string='Thời gian bắt đầu')
    end_time = fields.Datetime(string='Thời gian kết thúc')
    room_id = fields.Many2one('beauty.room', string='Phòng điều trị')
    doctor_id = fields.Many2one('hr.employee', string='Bác sĩ', domain=[('role_type', '=', 'doctor')])
    ktv_id = fields.Many2one('hr.employee', string='Kỹ thuật viên (KTV)', domain=[('role_type', '=', 'ktv')])
