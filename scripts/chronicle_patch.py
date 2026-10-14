from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()

def read_file(relative):
    path = ROOT / relative
    if not path.is_file():
        raise RuntimeError(f"Required file not found: {relative}")
    return path.read_text()

def backup_file(relative):
    source = ROOT / relative
    destination = ROOT / "backups" / (
        source.name + ".before_chronicle_patch"
    )
    if not destination.exists():
        shutil.copy2(source, destination)
        print(f"Backup created: {destination.relative_to(ROOT)}")

def write_file(relative, content):
    (ROOT / relative).write_text(content)
    print(f"Updated: {relative}")

def main():
    pubspec = read_file("pubspec.yaml")
    manifest = read_file("android/app/src/main/AndroidManifest.xml")
    gradle = read_file("android/app/build.gradle.kts")

    # Validate the expected project structure before changing anything.
    if not re.search(r"(?m)^dependencies:\s*$", pubspec):
        raise RuntimeError("Could not find dependencies: in pubspec.yaml")

    if "cupertino_icons:" not in pubspec:
        raise RuntimeError(
            "Could not find cupertino_icons in pubspec.yaml; "
            "no files were changed."
        )

    if 'android:label="chronicle_ai"' not in manifest:
        raise RuntimeError(
            "Expected Android app label was not found; "
            "no files were changed."
        )

    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        raise RuntimeError(
            "Expected launcher icon declaration was not found; "
            "no files were changed."
        )

    if "minSdk = flutter.minSdkVersion" not in gradle:
        raise RuntimeError(
            "Expected minSdk declaration was not found; "
            "no files were changed."
        )

    # Make backups before applying any changes.
    for filename in (
        "pubspec.yaml",
        "android/app/src/main/AndroidManifest.xml",
        "android/app/build.gradle.kts",
    ):
        backup_file(filename)

    # Add dependencies only if they are not already present.
    dependency_block = """
  ffmpeg_kit_flutter_new_min: ^3.6.7
  path_provider: ^2.1.5
  share_plus: ^12.0.1
"""

    if "ffmpeg_kit_flutter_new_min:" not in pubspec:
        pubspec = pubspec.replace(
            "  cupertino_icons: ^1.0.8\n",
            "  cupertino_icons: ^1.0.8\n" + dependency_block,
            1,
        )

    # Use the project name shown to Android users and our custom icon.
    manifest = manifest.replace(
        'android:label="chronicle_ai"',
        'android:label="Chronicle AI"',
        1,
    )
    manifest = manifest.replace(
        'android:icon="@mipmap/ic_launcher"',
        'android:icon="@drawable/chronicle_launcher"',
        1,
    )

    # FFmpeg Kit requires Android API 24 or newer.
    gradle = gradle.replace(
        "minSdk = flutter.minSdkVersion",
        "minSdk = 24",
        1,
    )

    write_file("pubspec.yaml", pubspec)
    write_file("android/app/src/main/AndroidManifest.xml", manifest)
    write_file("android/app/build.gradle.kts", gradle)

    icon = ROOT / "android/app/src/main/res/drawable/chronicle_launcher.xml"
    renderer = ROOT / "lib/services/video_exporter.dart"

    if not icon.is_file():
        raise RuntimeError(
            "The custom icon file is missing: "
            "android/app/src/main/res/drawable/chronicle_launcher.xml"
        )

    if not renderer.is_file():
        raise RuntimeError(
            "The video renderer is missing: lib/services/video_exporter.dart"
        )

    print("\nPatch completed.")
    print("App label: Chronicle AI")
    print("Launcher icon: custom Chronicle AI icon")
    print("Android minimum SDK: 24")
    print("Dependencies: FFmpeg Kit, path_provider, share_plus")
    print("\nThe video renderer still needs to be connected to the app UI.")
    print("No APK was built by this script.")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nPATCH STOPPED: {error}", file=sys.stderr)
        sys.exit(1)
