from odoo import models, fields, api
from datetime import timedelta
import pytz

class BeautyAppointment(models.Model):
    _inherit = 'beauty.appointment'

    # Các cờ kiểm soát Cron job không chạy lặp lại
    reminder_sent = fields.Boolean(string='Đã gửi nhắc hẹn', default=False, tracking=True)
    late_alert_sent = fields.Boolean(string='Đã cảnh báo trễ', default=False, tracking=True)

    def write(self, vals):
        res = super(BeautyAppointment, self).write(vals)
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
        """Chuyển đổi giờ từ hệ thống (UTC) sang giờ Việt Nam (Asia/Ho_Chi_Minh)"""
        if not self.start_time:
            return ''
        user_tz = pytz.timezone(self.env.user.tz or 'Asia/Ho_Chi_Minh')
        local_time = pytz.utc.localize(self.start_time).astimezone(user_tz)
        return local_time.strftime('%H:%M ngày %d/%m/%Y')

    def _simulate_auto_send_message(self, msg_type):
        """Mô phỏng hệ thống nhắn tin bằng cách in log vào Chatter (thay thế cho SMS thật)"""
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
            body=html_body,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def _notify_staff_arrival(self):
        """Giao việc (Task) cho nhân sự chuyên môn khi khách tới cửa"""
        users_to_notify = []
        if self.doctor_id and self.doctor_id.user_id:
            users_to_notify.append(self.doctor_id.user_id)
        if self.ktv_id and self.ktv_id.user_id:
            users_to_notify.append(self.ktv_id.user_id)
        
        for user in set(users_to_notify): # set() để loại bỏ trùng lặp nếu Bác sĩ kiêm KTV
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='Khách hàng đã đến - Vui lòng tiếp đón',
                note=f'Khách hàng <b>{self.customer_id.name}</b> đã check-in. Vui lòng chuẩn bị phòng <b>{self.room_id.name or "điều trị"}</b> để tiếp đón.',
                user_id=user.id
            )

    @api.model
    def _cron_remind_upcoming_appointments(self):
        """11.2: Quét lịch ngày mai và tự động bắn log nhắc nhở"""
        now = fields.Datetime.now()
        tomorrow_start = now + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(hours=24)
        
        upcoming_appointments = self.search([
            ('state', '=', 'confirmed'),
            ('start_time', '>=', tomorrow_start),
            ('start_time', '<=', tomorrow_end),
            ('reminder_sent', '=', False)
        ])
        
        for app in upcoming_appointments:
            app._simulate_auto_send_message('remind')
            app.reminder_sent = True

    @api.model
    def _cron_alert_late_appointments(self):
        """11.3: Quét khách trễ hẹn và tạo Task Cảnh báo cho Lễ tân gọi điện"""
        now = fields.Datetime.now()
        late_appointments = self.search([
            ('state', '=', 'confirmed'),
            ('start_time', '<', now),
            ('late_alert_sent', '=', False)
        ])
        
        if not late_appointments:
            return

        # Lấy danh sách user thuộc nhóm Lễ tân (Dựa trên XML ID từ beauty_security.xml)
        reception_group = self.env.ref('ht_beauty_core.beauty_group_receptionist', raise_if_not_found=False)
        if not reception_group or not reception_group.users:
            return

        reception_users = reception_group.users
        for app in late_appointments:
            for user in reception_users:
                app.activity_schedule(
                    'mail.mail_activity_data_warning',
                    summary='CẢNH BÁO: Khách trễ hẹn!',
                    note=f'Khách hàng <b>{app.customer_id.name}</b> đã trễ lịch hẹn lúc {app._get_formatted_time()}. Vui lòng gọi điện kiểm tra xem khách có đang trên đường đến không.',
                    user_id=user.id
                )
            app.late_alert_sent = True