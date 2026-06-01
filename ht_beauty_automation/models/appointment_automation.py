# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta
from markupsafe import Markup  
import pytz

class BeautyAppointmentAutomation(models.Model):
    _inherit = 'beauty.appointment'

    reminder_sent = fields.Boolean(string='Đã gửi nhắc hẹn', default=False, tracking=True)
    late_alert_sent = fields.Boolean(string='Đã cảnh báo trễ', default=False, tracking=True)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if 'state' in vals:
                # 11.1: Tự động gửi tin nhắn xác nhận khi Lễ tân chốt lịch
                if vals['state'] == 'confirmed':
                    rec._simulate_auto_send_message('confirm')
                
                # 11.4: Tự động bắn thông báo cho Bác sĩ/KTV khi Lễ tân check-in "Đã đến"
                elif vals['state'] == 'arrived':
                    rec._notify_staff_arrival()
        return res

    def _get_formatted_time(self):
        if not self.start_time:
            return ''
        user_tz = pytz.timezone(self.env.user.tz or 'Asia/Ho_Chi_Minh')
        local_time = pytz.utc.localize(self.start_time).astimezone(user_tz)
        return local_time.strftime('%H:%M ngày %d/%m/%Y')

    def _simulate_auto_send_message(self, msg_type):
        app_time = self._get_formatted_time()
        customer_name = self.customer_id.name or 'Quý khách'

        if msg_type == 'confirm':
            subject = 'HỆ THỐNG ĐÃ TỰ ĐỘNG GỬI TIN NHẮN XÁC NHẬN LỊCH HẸN'
            content = f"""
                <b>Dạ chào {customer_name},</b><br/>
                HT Beauty xin xác nhận lịch hẹn của bạn đã được đặt thành công.<br/>
                - Thời gian: <b>{app_time}</b><br/>
                Bạn nhớ đến đúng giờ để spa chuẩn bị chu đáo nhất nhé. Cần hỗ trợ thêm bạn cứ phản hồi lại nha!<br/>
                Cảm ơn bạn!
            """
        elif msg_type == 'remind':
            subject = 'HỆ THỐNG ĐÃ TỰ ĐỘNG GỬI TIN NHẮN NHẮC LỊCH HẸN NGÀY MAI'
            content = f"""
                <b>Dạ chào {customer_name},</b><br/>
                HT Beauty xin nhắc nhẹ bạn có lịch hẹn vào <b>{app_time}</b> ngày mai nhé.<br/>
                Nếu có thay đổi về thời gian, bạn phản hồi lại tin nhắn này giúp spa nha.<br/>
                Hẹn gặp bạn tại HT Beauty!
            """
        else:
            return

        html_body = f"<div style='background-color: #e6f2ff; padding: 10px; border-radius: 5px; border-left: 4px solid #005ce6;'><h4 style='color: #005ce6; margin-top: 0;'>[🤖 {subject}]</h4>{content}</div>"
        
        self.message_post(
            body=Markup(html_body),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def _notify_staff_arrival(self):
        """Giao việc (Task) cho nhân sự chuyên môn khi khách tới cửa (Bản có chẩn đoán lỗi)"""
        for rec in self:
            staff_members = []
            if rec.doctor_id:
                staff_members.append(('Bác sĩ', rec.doctor_id))
            if rec.ktv_id:
                staff_members.append(('Kỹ thuật viên', rec.ktv_id))
            
            for role, staff in staff_members:
                # Kiểm tra xem nhân viên đã được gắn User đăng nhập chưa
                if staff.user_id:
                    # 1. Tạo Activity Task To-do
                    rec.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=f'[{role}] Khách hàng đã đến - Vui lòng tiếp đón',
                        note=f'Khách hàng <b>{rec.customer_id.name}</b> đã check-in. Vui lòng chuẩn bị phòng <b>{rec.room_id.name or "điều trị"}</b>.',
                        user_id=staff.user_id.id
                    )
                    # 2. Bắn log báo thành công vào Chatter và Tag tên để 100% có chuông thông báo
                    rec.message_post(
                        body=Markup(f"🔔 Đã tự động giao việc cho {role}: <b>@{staff.user_id.name}</b> ra đón khách."),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
                else:
                    # 3. NẾU LỖI THIẾU TÀI KHOẢN -> BÁO ĐỎ NGAY LẬP TỨC TRÊN CHATTER
                    rec.message_post(
                        body=Markup(f"<div style='color: red;'>⚠️ <b>HỆ THỐNG TỪ CHỐI GIAO VIỆC:</b> Không thể gửi thông báo cho {role} <b>{staff.name}</b> vì nhân sự này chưa được liên kết với tài khoản đăng nhập (User). Lễ tân vui lòng gọi điện trực tiếp để báo khách đến!</div>"),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )

    @api.model
    def _cron_remind_upcoming_appointments(self):
        now_utc = fields.Datetime.now()
        user_tz = pytz.timezone(self.env.user.tz or 'Asia/Ho_Chi_Minh')
        now_local = pytz.utc.localize(now_utc).astimezone(user_tz)
        tomorrow_local = now_local + timedelta(days=1)
        
        start_of_tomorrow_local = tomorrow_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_tomorrow_local = tomorrow_local.replace(hour=23, minute=59, second=59, microsecond=0)
        
        utc_start = start_of_tomorrow_local.astimezone(pytz.utc).replace(tzinfo=None)
        utc_end = end_of_tomorrow_local.astimezone(pytz.utc).replace(tzinfo=None)
        
        upcoming_appointments = self.search([
            ('state', '=', 'confirmed'),
            ('start_time', '>=', utc_start),
            ('start_time', '<=', utc_end),
            ('reminder_sent', '=', False)
        ])
        
        for app in upcoming_appointments:
            app._simulate_auto_send_message('remind')
            app.reminder_sent = True

    @api.model
    def _cron_alert_late_appointments(self):
        """11.3: Quét khách trễ hẹn và tạo Task Gọi điện cho Lễ tân, in log ra Chatter"""
        now = fields.Datetime.now()
        late_appointments = self.search([
            ('state', '=', 'confirmed'),
            ('start_time', '<', now),
            ('late_alert_sent', '=', False)
        ])
        
        if not late_appointments:
            return

        reception_group = self.env.ref('ht_beauty_core.beauty_group_receptionist', raise_if_not_found=False)
        reception_users = self.env['res.users'].search([('group_ids', 'in', reception_group.id)]) if reception_group else []

        for app in late_appointments:
            if reception_users:
                for user in reception_users:
                    # SỬA LỖI Ở ĐÂY: Dùng mã chuẩn mail.mail_activity_data_call của Odoo
                    app.activity_schedule(
                        'mail.mail_activity_data_call',
                        summary='CẢNH BÁO: Khách trễ hẹn!',
                        note=f'Khách hàng <b>{app.customer_id.name}</b> đã trễ lịch hẹn lúc {app._get_formatted_time()}. Vui lòng gọi điện kiểm tra.',
                        user_id=user.id
                    )
                # Bắn dòng chữ màu cam ra Chatter để dễ dàng nhìn thấy kết quả Test
                app.message_post(
                    body=Markup(f"<div style='color: #d97706; background-color: #fef3c7; padding: 10px; border-radius: 5px; border-left: 4px solid #d97706;'>⚠️ <b>HỆ THỐNG CẢNH BÁO TRỄ HẸN:</b> Đã tự động tạo công việc yêu cầu Lễ tân gọi điện xác nhận tình trạng của khách hàng.</div>"),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
            else:
                # Nếu không tìm thấy user Lễ tân nào, báo lỗi màu đỏ
                app.message_post(
                    body=Markup(f"<div style='color: red; padding: 10px; border-radius: 5px; border-left: 4px solid red;'>⚠️ <b>LỖI HỆ THỐNG:</b> Khách đã trễ hẹn nhưng không tìm thấy tài khoản Lễ tân nào để giao việc!</div>"),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
            
            app.late_alert_sent = True