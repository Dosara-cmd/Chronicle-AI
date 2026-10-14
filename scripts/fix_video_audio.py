from pathlib import Path

renderer_path = Path("lib/services/video_exporter.dart")
main_path = Path("lib/main.dart")

renderer = renderer_path.read_text()
main = main_path.read_text()

# Add the standard Dart libraries needed for generating a WAV soundtrack.
if "import 'dart:math' as math;" not in renderer:
    renderer = renderer.replace(
        "import 'dart:io';",
        "import 'dart:io';\nimport 'dart:math' as math;\nimport 'dart:typed_data';",
        1,
    )

# Fix the non-constant expressions inside const constructors.
renderer = renderer.replace(
    "const Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble())",
    "Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble())",
)

renderer = renderer.replace(
    "final bounds = const Rect.fromLTWH(",
    "final bounds = Rect.fromLTWH(",
)

renderer = renderer.replace(
    "const ui.Gradient.linear(",
    "ui.Gradient.linear(",
)

# Replace the video-only FFmpeg command with video + generated audio.
old_command = '''      final command =
          "-y -f concat -safe 0 "
          "-i '${concatFile.path}' "
          '-vf "$filter" '
          '-c:v mpeg4 '
          '-q:v 5 '
          '-r $framesPerSecond '
          '-t $totalSeconds '
          '-movflags +faststart '
          "'${output.path}'";
'''

new_command = '''      final ambientAudio = File(
        '${workDirectory.path}/cinematic_ambient.wav',
      );

      await _writeAmbientWav(
        file: ambientAudio,
        durationSeconds: totalSeconds,
      );

      final command =
          "-y "
          "-f concat -safe 0 "
          "-i '${concatFile.path}' "
          "-i '${ambientAudio.path}' "
          '-vf "$filter" '
          '-map 0:v:0 '
          '-map 1:a:0 '
          '-c:v mpeg4 '
          '-q:v 5 '
          '-r $framesPerSecond '
          '-c:a aac '
          '-b:a 96k '
          '-af "volume=0.75" '
          '-t $totalSeconds '
          '-shortest '
          '-movflags +faststart '
          "'${output.path}'";
'''

if old_command not in renderer:
    raise SystemExit(
        "STOP: The expected FFmpeg command was not found. "
        "No renderer changes were saved. Please share the current "
        "section around 'final command'."
    )

renderer = renderer.replace(old_command, new_command, 1)

# Insert a local WAV generator. It creates a soft, layered ambient drone
# with a gradual fade-in and fade-out. No external audio file is needed.
marker = "  static Future<void> _drawSceneCard({"

audio_method = r'''  static Future<void> _writeAmbientWav({
    required File file,
    required int durationSeconds,
  }) async {
    const sampleRate = 22050;
    const channels = 2;
    const bytesPerSample = 2;
    const bytesPerFrame = channels * bytesPerSample;

    final totalFrames = durationSeconds * sampleRate;
    final dataSize = totalFrames * bytesPerFrame;

    // Standard 44-byte PCM WAV header.
    final header = ByteData(44);

    void writeAscii(int offset, String value) {
      for (var i = 0; i < value.length; i++) {
        header.setUint8(offset + i, value.codeUnitAt(i));
      }
    }

    writeAscii(0, 'RIFF');
    header.setUint32(4, 36 + dataSize, Endian.little);
    writeAscii(8, 'WAVE');
    writeAscii(12, 'fmt ');
    header.setUint32(16, 16, Endian.little);
    header.setUint16(20, 1, Endian.little);
    header.setUint16(22, channels, Endian.little);
    header.setUint32(24, sampleRate, Endian.little);
    header.setUint32(28, sampleRate * bytesPerFrame, Endian.little);
    header.setUint16(32, bytesPerFrame, Endian.little);
    header.setUint16(34, 16, Endian.little);
    writeAscii(36, 'data');
    header.setUint32(40, dataSize, Endian.little);

    final handle = await file.open(mode: FileMode.write);

    try {
      await handle.writeFrom(header.buffer.asUint8List());

      const framesPerChunk = 4096;
      var frame = 0;

      while (frame < totalFrames) {
        final chunkFrames = math.min(
          framesPerChunk,
          totalFrames - frame,
        );

        final chunk = ByteData(chunkFrames * bytesPerFrame);

        for (var i = 0; i < chunkFrames; i++) {
          final currentFrame = frame + i;
          final time = currentFrame / sampleRate;

          // A gentle cinematic bed made from three low-volume tones.
          final tone =
              math.sin(2 * math.pi * 110.0 * time) * 0.42 +
              math.sin(2 * math.pi * 164.81 * time) * 0.30 +
              math.sin(2 * math.pi * 220.0 * time) * 0.20;

          // Slowly moving amplitude prevents the sound from feeling
          // completely static while keeping it subtle beneath narration.
          final movement =
              0.82 + 0.18 * math.sin(2 * math.pi * 0.075 * time);

          final fadeIn = math.min(1.0, time / 3.0);
          final remaining = durationSeconds - time;
          final fadeOut = math.min(1.0, remaining / 4.0);

          final envelope = math.min(fadeIn, fadeOut);
          final normalized = (tone * movement * envelope * 0.12)
              .clamp(-1.0, 1.0);

          final sample = (normalized * 32767).round();
          final offset = i * bytesPerFrame;

          // Duplicate the same ambience into left and right channels.
          chunk.setInt16(offset, sample, Endian.little);
          chunk.setInt16(offset + 2, sample, Endian.little);
        }

        await handle.writeFrom(
          chunk.buffer.asUint8List(0, chunk.lengthInBytes),
        );

        frame += chunkFrames;
      }
    } finally {
      await handle.close();
    }
  }

'''

if marker not in renderer:
    raise SystemExit(
        "STOP: Could not find _drawSceneCard. "
        "No renderer changes were saved."
    )

if "_writeAmbientWav({" not in renderer:
    renderer = renderer.replace(marker, audio_method + marker, 1)

# Confirm the intended fixes exist before saving.
if "const Rect.fromLTWH(0, 0, width.toDouble()" in renderer:
    raise SystemExit("STOP: A non-constant Rect expression remains.")

if "const ui.Gradient.linear(" in renderer:
    raise SystemExit("STOP: A non-constant Gradient expression remains.")

if "-c:a aac" not in renderer or "_writeAmbientWav({" not in renderer:
    raise SystemExit("STOP: Audio integration did not complete.")

renderer_path.write_text(renderer)

# Remove the unnecessary direct import. share_plus exports XFile.
main = main.replace(
    "import 'package:cross_file/cross_file.dart';\n",
    "",
)
main_path.write_text(main)

print("PATCH_OK: Fixed const expressions.")
print("PATCH_OK: Added locally generated ambient WAV soundtrack.")
print("PATCH_OK: Connected soundtrack to MP4 export.")
print("PATCH_OK: Removed unnecessary cross_file import.")
