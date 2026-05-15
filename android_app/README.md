# YT Downloader Android

Android WebView wrapper for the Django YT Downloader project.

## How it works

The APK opens the Django website inside a WebView. Video processing still runs on
the Django server, so the phone and the computer must be on the same network.

## Run the Django server for a real phone

Find your computer local IP address:

```powershell
ipconfig
```

Start Django on all local network interfaces:

```powershell
python manage.py runserver 0.0.0.0:8000
```

In the Android app, enter:

```text
http://YOUR_COMPUTER_IP:8000/
```

For example:

```text
http://192.168.1.10:8000/
```

## Build APK in Android Studio

1. Open the `android_app` folder in Android Studio.
2. Wait for Gradle sync to finish.
3. Use `Build > Build Bundle(s) / APK(s) > Build APK(s)`.
4. The APK will be created in `app/build/outputs/apk/debug/`.

The app allows HTTP traffic for local lab testing. For a public deployment, host
the Django project on HTTPS and use that HTTPS URL in the app.
