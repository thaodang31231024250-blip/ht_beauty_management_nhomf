{
    'name': 'HT Beauty Automation',
    'version': '1.0',
    'category': 'HT Beauty',
    'summary': 'Tự động hóa thông báo, nhắc lịch và tạo task chăm sóc khách hàng cho HT Beauty',
    'author': 'Nhóm F',
    'depends': [
        'mail', 
        'ht_beauty_core', 
        'ht_beauty_appointment', 
        'ht_beauty_treatment'
    ],
    'data': [
        'data/automation_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}