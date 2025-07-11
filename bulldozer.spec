[app]
title = My Jarvis
package.name = myjarvis
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,spec
version = 0.1
requirements = python3,kivy,openai,speechrecognition,pyttsx3,pyaudio
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.0.0
android.permissions = RECORD_AUDIO, INTERNET
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
