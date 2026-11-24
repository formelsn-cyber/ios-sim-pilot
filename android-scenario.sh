#!/bin/bash
mkdir -p shots
adb root || true
sleep 3
adb shell "echo '_ --disable-fre --no-first-run --no-default-browser-check' > /data/local/tmp/chrome-command-line"
adb shell chmod 755 /data/local/tmp/chrome-command-line
adb shell am set-debug-app --persistent com.android.chrome
adb shell am force-stop com.android.chrome
adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/" com.android.chrome
sleep 35
# secours : si l'ecran de bienvenue reste, appuyer sur "Use without an account" puis fermer les invites
adb shell input tap 540 2093; sleep 4
adb shell input tap 540 2093; sleep 4
adb exec-out screencap -p > shots/a01-home.png
adb shell uiautomator dump /sdcard/ui.xml; adb pull /sdcard/ui.xml shots/a01-ui.xml
for p in modeles tissus; do
  adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/$p/" com.android.chrome
  sleep 25
  adb exec-out screencap -p > shots/a02-$p.png
done
adb shell am start -a android.intent.action.VIEW -d "https://yombal.sn/yombal-manifest.webmanifest" com.android.chrome
sleep 15
adb exec-out screencap -p > shots/a03-manifest.png
adb shell getprop ro.build.version.release > shots/android-version.txt
