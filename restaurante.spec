# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Recopilar TODOS los submódulos de apps explícitamente
apps_submodules = collect_submodules('apps')

hiddenimports = [
    'environ', 'django_environ', 'environ.environ',
    'config', 'config.settings', 'config.urls', 'config.wsgi', 'config.asgi',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.core.cache.backends.locmem.LocMemCache',
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.template.context_processors.auth',
    'django.template.context_processors.messages',
    'apps.core.context_processors.mesas_en_limpieza',
    'PIL', 'PIL.Image',
] + apps_submodules + (
    collect_submodules('django')
    + collect_submodules('axes')
    + collect_submodules('simple_history')
    + collect_submodules('whitenoise')
    + collect_submodules('waitress')
)

# Recopilar archivos de datos de apps (templates, static, etc.)
apps_datas = collect_data_files('apps', include_py_files=False)

datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('icons', 'icons'),
] + apps_datas

a = Analysis(
    ['desktop/launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'pytest'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Restaurante',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Mantener True para debugging
    icon='icons/icono.ico' if __import__('os').path.exists('icons/icono.ico') else None,
    disable_windowed_traceback=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='Restaurante',
)