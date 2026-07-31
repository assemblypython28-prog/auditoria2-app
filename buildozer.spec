[app]

# (str) Title of your application
title = Auditoria de Ativos

# (str) Package name
package.name = auditoriaativos

# (str) Package domain (reverse DNS)
package.domain = org.auditoria

# (str) Source code directory
source.dir = .

# (list) Source files to include (separated by commas)
source.include_exts = py,png,jpg,kv,atlas,db,ttf

# (list) Exclude these files/folders
source.exclude_exts = spec,pyc,pyo,pyd

# (list) List of dependencies (Python packages)
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,openpyxl,requests,setuptools

# (str) python-for-android branch to use (needed for NDK 28c compatibility fixes for pandas/numpy)
p4a.branch = develop

# (str) Custom version (semantic)
version = 1.0.0

# (bool) Allow user to resize the window (desktop only)
resizable = False

# (str) Orientation (portrait, landscape, or both)
orientation = portrait

# (int) Target Android API level
android.api = 30

# (int) Minimum Android API level
android.minapi = 24

# (int) Android SDK version
android.sdk_version = 30

# (bool) Accept Android SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX (required for modern Kivy)
android.enable_androidx = True

# (list) Permissions required by the app
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (str) Android architecture(s)
android.arch = armeabi-v7a, arm64-v8a

# (bool) Allow backup of app data
android.allow_backup = True

[buildozer]

# (int) Log level
log_level = 2

# (bool) Warn if a required build tool is missing
warn_on_missing = 1
