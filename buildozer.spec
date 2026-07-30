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
# IMPORTANTE: adicione o pandas e openpyxl
requirements = python3,kivy==2.1.0,pandas,openpyxl,requests,setuptools

# (str) Custom version (semantic)
version = 1.0.0

# (bool) Allow user to resize the window (desktop only)
resizable = False

# (str) Orientation (portrait, landscape, or both)
orientation = portrait

# (list) Supported orientations (Android only)
# orientations = portrait,landscape

# (int) Target Android API level
android.api = 30

# (int) Minimum Android API level
android.minapi = 21

# (int) Android SDK version
android.sdk_version = 30

# (bool) Accept Android SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX (required for modern Kivy)
android.enable_androidx = True

# (list) Permissions required by the app
# INTERNET: pode ser necessário para algumas bibliotecas (pandas/requests), mas não é obrigatório.
# READ/WRITE_EXTERNAL_STORAGE: necessário para ler/salvar arquivos Excel.
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (str) Android architecture(s) (armeabi-v7a, arm64-v8a, x86, x86_64)
android.arch = armeabi-v7a, arm64-v8a

# (bool) Allow backup of app data
android.allow_backup = True

# (str) Full name of the Android activity class
# android.entitlement =

# (str) Android theme (material, etc.)
# android.theme = @android:style/Theme.Material.Light.NoActionBar

# (list) Gradle dependencies (e.g., com.android.support:appcompat-v7:28.0.0)
# android.gradle_dependencies =

# (list) Android Java classes to add
# android.add_src =

# (str) Python for android (p4a) branch
# p4a.branch = master

# (str) Android NDK version (e.g., 23b)
# android.ndk = 23b

# (str) Android SDK directory (auto-detected if not set)
# android.sdk_path =

# (str) Android NDK directory (auto-detected if not set)
# android.ndk_path =

# (str) Android ANT directory (auto-detected if not set)
# android.ant_path =

# (list) Java source files to include
# android.add_src =

# (list) JAR files to include
# android.add_jar =

# (list) AAR files to include
# android.add_aar =

# (str) Python for Android distribution name
# p4a.distribution = kivy

# (str) Bootstrap to use (sdl2, webview, etc.)
# android.bootstrap = sdl2

# (str) Window background color (hex)
# android.window_background_color = #ffffff

# (str) Presplash background color (hex)
# android.presplash_color = #1E293B

# (str) Presplash image file
# android.presplash_image = presplash.png

# (str) Icon image file (must be 512x512)
# android.icon = icon.png

# (str) Adaptive icon foreground
# android.adaptive_icon_foreground = icon-foreground.png

# (str) Adaptive icon background
# android.adaptive_icon_background = #1E293B

# (str) iOS Bundle identifier
# ios.bundle_identifier = org.auditoria.auditoriaativos

# (str) iOS version (e.g., 13.0)
# ios.min_version = 13.0

# (list) iOS frameworks
# ios.frameworks =

# (list) iOS plist keys
# ios.plist_keys =

# (bool) Enable iOS debug mode
# ios.debug = False

# (str) macOS version
# osx.python_version = 3

# (str) macOS Kivy version
# osx.kivy_version = 2.1.0

# (bool) Create a Windows app instead of console
# windows.console = False

# (bool) Create a Windows installer
# windows.installer = False

# (str) Windows icon file
# windows.icon = icon.ico

# (str) Windows exe version
# windows.version = 1.0.0.0

# (str) Windows company name
# windows.company = MyCompany

# (str) Windows copyright
# windows.copyright = Copyright (c) 2025 Robespierre Santana Silva

# (bool) Linux desktop app (requires PyInstaller)
# linux.desktop = True

# (str) Linux desktop icon
# linux.icon = icon.png

# (str) Linux desktop categories
# linux.categories = Office;Utility;

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug, 3 = trace)
log_level = 2

# (bool) Warn if a required build tool is missing
warn_on_missing = 1

# (list) Paths to search for build tools
# build_tools_paths = /usr/bin

# (str) Directory where buildozer stores source files
# build_dir = ./buildozer

# (str) Directory where the app is stored
# app_dir = ./

# (str) Directory where the build artifacts are stored
# dist_dir = ./dist

# (str) Directory where the release APK/AAB is stored
# release_dir = ./bin

# (str) Buildozer log file
# log_file = ./buildozer.log

# (bool) Keep the build directory after the build
# keep_build_dir = False

# (bool) Use the accelerated Android emulator
# use_emulator = False

# (bool) Show debug messages from the Android app
# android.debug = False

# (bool) Run the app after build
# run = True

# (str) Custom command to run the app (e.g., adb shell am start)
# run_command = adb shell am start -n {package.domain}/{package.domain}.{package.name}/{package.domain}.{package.name}.{package.name}Activity

# (str) Custom command to deploy the app (e.g., adb install -r)
# deploy_command = adb install -r

# (str) Custom command to log the app (e.g., adb logcat)
# log_command = adb logcat | grep python