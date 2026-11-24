#!/bin/bash
mkdir -p shots
adb shell settings put global window_animation_scale 0
adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/" com.android.chrome 2>&1 || adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/"
sleep 40
adb exec-out screencap -p > shots/a01-home.png
adb shell uiautomator dump /sdcard/ui.xml; adb pull /sdcard/ui.xml shots/a01-ui.xml
adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/modeles/"
sleep 25
adb exec-out screencap -p > shots/a02-modeles.png
adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/tissus/"
sleep 25
adb exec-out screencap -p > shots/a03-tissus.png
adb shell getprop ro.build.version.release > shots/android-version.txt
