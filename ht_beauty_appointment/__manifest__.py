{
    'name': 'HT Beauty Appointment',
    'version': '1.0',
    'category': 'HT Beauty',
    'author': 'Nhóm F',
    'license': 'LGPL-3',
    'summary': 'Phần mềm quản lý đặt lịch hẹn và điều phối tài nguyên cho HT Beauty',
    'description': ''''''
    'Chức năng của phân hệ:'
    '- Đặt lịch hẹn tư vấn và lịch hẹn điều trị'
    '- Điều phối tài nguyên'
    '- Các chức năng ngăn xung đột tài nguyên khi đặt lịch',
    'depends': ['ht_beauty_core', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}