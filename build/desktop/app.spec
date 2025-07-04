# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['/Users/tonganle/Documents/GitHub/AI_Truck/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('/Users/tonganle/Documents/GitHub/AI_Truck/templates', 'templates'),
        ('/Users/tonganle/Documents/GitHub/AI_Truck/static', 'static'),
        ('/Users/tonganle/Documents/GitHub/AI_Truck/video_processor.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'openai',
        'dashscope',
        'moviepy',
        'alibabacloud_alimt20181012',
        'alibabacloud_tea_openapi',
        'alibabacloud_tea_util',
        'playsound',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI视频处理工具',
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
    icon='../static/icon.ico' if os.path.exists('../static/icon.ico') else None,
)
