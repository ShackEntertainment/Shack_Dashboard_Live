import os
p = r'C:\Users\Bola\Documents\Shack_Project\Scripts\shack_mail_bridge.py'
src = open(p, encoding='utf-8').read()
i = src.find('ACCOUNTS = {')
j = src.find('\n}', i)
if i == -1 or j == -1:
    print('FATAL: ACCOUNTS block not found')
else:
    NEW = '''ACCOUNTS = {
    'a-r':  {'user_env': 'MAIL_AR_USER',  'pass_env': 'MAIL_AR_PASS',
             'kind': 'talent'},
    'b2b':  {'user_env': 'MAIL_B2B_USER', 'pass_env': 'MAIL_B2B_PASS',
             'kind': 'partner'},
    'info': {'user_env': 'MAIL_INFO_USER', 'pass_env': 'MAIL_INFO_PASS',
             'kind': 'general'},
    'amit': {'user_env': 'MAIL_AMIT_USER', 'pass_env': 'MAIL_AMIT_PASS',
             'kind': 'general'},
    'bola': {'user_env': 'MAIL_BOLA_USER', 'pass_env': 'MAIL_BOLA_PASS',
             'kind': 'general'},
    'leo':  {'user_env': 'MAIL_LEO_USER',  'pass_env': 'MAIL_LEO_PASS',
             'kind': 'general'},
}'''
    src = src[:i] + NEW + src[j + 2:]
    open(p, 'w', encoding='utf-8').write(src)
    print('ACCOUNTS rewritten OK')