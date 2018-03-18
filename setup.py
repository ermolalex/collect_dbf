# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

company_name = 'Kik-soft'
product_name = 'Simple-POS'

build_exe_options = {
    'includes': ['atexit', 'PySide.QtNetwork'],
    'include_msvcr': True,
    }

base = None

exe = Executable(script='spos.py',
                 base=base,
                 icon='python.ico',
                 shortcutName='SimplePOS',
                 shortcutDir='DesktopFolder',
                )

setup(name=product_name,
      version='0.1.0',
      description=u'Простая программа для сбора dbf-файлов в базу данных SQLite',
      executables = [Executable("collect_dbf.py")]
#      options={'build_exe': build_exe_options}
)