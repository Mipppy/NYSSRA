# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\Tim\\AppData\\Local\\Programs\\Python\\Python312-32\\Lib\\site-packages'],
    binaries=[],
    datas=[('render.py', '.'), ('rendering', 'rendering'), ('webserver_static', 'webserver_static')],
    hiddenimports=['PyQt5.QtWidgets', 'jaraco', 'jaraco.classes', 'jaraco.packaging', 'jaraco.text', 'websocket'],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
