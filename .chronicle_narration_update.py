from pathlib import Path
from datetime import datetime
import shutil
import sys

root = Path.cwd()
main_path = root / "lib/main.dart"
exporter_path = root / "lib/services/video_exporter.dart"
manifest_path = root / "android/app/src/main/AndroidManifest.xml"
pubspec_path = root / "pubspec.yaml"
service_path = root / "lib/services/narration_service.dart"

paths = [main_path, exporter_path, manifest_path, pubspec_path]
if any(not p.is_file() for p in paths):
    sys.exit("STOP: A required project file is missing.")

main, exporter, manifest, pubspec = [p.read_text() for p in paths]

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)

try:
    if service_path.exists():
        raise ValueError("Narration service already exists; refusing to overwrite.")

    pubspec = replace_once(
        pubspec,
        "  cross_file: ^0.3.5+5",
        "  cross_file: ^0.3.5+5\n  flutter_tts: ^4.2.5",
        "TTS dependency",
    )

    main = replace_once(
        main,
        "import 'services/video_exporter.dart';",
        "import 'services/video_exporter.dart';\n"
        "import 'services/narration_service.dart';",
        "Narration import",
    )

    if "android.intent.action.TTS_SERVICE" not in manifest:
        manifest = replace_once(
            manifest,
            '        <intent>\n            <action android:name="android.intent.action.PROCESS_TEXT"/>',
            '        <intent>\n            <action android:name="android.intent.action.TTS_SERVICE" />\n'
            '        </intent>\n        <intent>\n'
            '            <action android:name="android.intent.action.PROCESS_TEXT"/>',
            "Android TTS query",
        )

    service = r"""import 'dart:io';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:path_provider/path_provider.dart';

class ChronicleNarrationService {
  static Future<List<String>> synthesizeSceneNarration({
    required List<String> sceneTexts,
    required String voice,
  }) async {
    if (sceneTexts.isEmpty) {
      throw ArgumentError('At least one scene is required.');
    }

    final tts = FlutterTts();
    final dir = await getTemporaryDirectory();
    final stamp = DateTime.now().microsecondsSinceEpoch;
    final paths = <String>[];
    var language = 'en-US';
    var rate = 0.42;
    var pitch = 0.82;

    switch (voice) {
      case 'Warm Storyteller': rate = 0.48; pitch = 1.08; break;
      case 'Dramatic Narrator': rate = 0.40; pitch = 0.82; break;
      case 'Calm Narrator': rate = 0.38; pitch = 0.96; break;
      case 'Energetic Narrator': rate = 0.57; pitch = 1.12; break;
      case 'Female Documentary': rate = 0.46; pitch = 1.15; break;
      case 'British English': language = 'en-GB'; rate = 0.45; break;
      case 'American English': language = 'en-US'; rate = 0.45; break;
      default: break;
    }

    try {
      await tts.awaitSynthCompletion(true);
      await tts.setLanguage(language);
      await tts.setSpeechRate(rate);
      await tts.setPitch(pitch);
      await tts.setVolume(1.0);

      for (var i = 0; i < sceneTexts.length; i++) {
        var text = sceneTexts[i].trim();
        if (text.isEmpty) text = 'Historical chapter ${i + 1}.';
        if (text.length > 3500) text = '${text.substring(0, 3497)}...';
        final file = File('${dir.path}/chronicle_voice_${stamp}_$i.wav');
        await tts.synthesizeToFile(text, file.path, true);
        if (!await file.exists() || await file.length() == 0) {
          throw Exception(
            'Narration audio was not created. Check your Android text-to-speech '
            'engine and installed English voice.',
          );
        }
        paths.add(file.path);
      }
      return paths;
    } catch (_) {
      await deleteFiles(paths);
      rethrow;
    } finally {
      await tts.stop();
    }
  }

  static Future<void> deleteFiles(List<String> paths) async {
    for (final path in paths) {
      try {
        final f = File(path);
        if (await f.exists()) await f.delete();
      } catch (_) {}
    }
  }
}
"""

    start = main.find("Future<void> renderAndShareVideo(")
    end = main.find("\nclass PreparationScreen", start)
    if start < 0 or end < 0:
        raise ValueError("Could not locate export function.")

    main = main[:start] + r"""Future<void> renderAndShareVideo(
  BuildContext context, {
  required String title,
  required List<String> sceneTitles,
  required String duration,
  required String description,
  required String voice,
}) async {
  var dialogOpen = false;
  final narrationPaths = <String>[];

  try {
    final match = RegExp(r'\d+').firstMatch(duration);
    final minutes = int.tryParse(match?.group(0) ?? '') ?? 3;
    if (sceneTitles.isEmpty || minutes < 1 || minutes > 5) {
      throw ArgumentError('Choose scenes and a duration from 1 to 5 minutes.');
    }

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const AlertDialog(
        backgroundColor: surface2,
        content: Row(children: [
          SizedBox(width: 24, height: 24,
            child: CircularProgressIndicator(color: gold)),
          SizedBox(width: 16),
          Expanded(child: Text('Creating narration and rendering video...')),
        ]),
      ),
    );
    dialogOpen = true;

    final seconds = minutes * 60;
    final perScene = (seconds + sceneTitles.length - 1) ~/ sceneTitles.length;
    narrationPaths.addAll(
      await ChronicleNarrationService.synthesizeSceneNarration(
        sceneTexts: sceneTitles,
        voice: voice,
      ),
    );

    final file = await ChronicleVideoExporter.exportTitleCardVideo(
      title: title,
      sceneTitles: sceneTitles,
      secondsPerScene: perScene,
      totalDurationSeconds: seconds,
      narrationAudioPaths: narrationPaths,
    );

    if (context.mounted && dialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
      dialogOpen = false;
    }
    if (!context.mounted) return;

    await SharePlus.instance.share(ShareParams(
      files: [XFile(file.path)],
      text: description.trim().isEmpty
          ? 'Created with Chronicle AI'
          : '${description.trim()}\n\nCreated with Chronicle AI',
      subject: title,
    ));
    if (context.mounted) showMessage(context, 'Video exported: ${file.path}');
  } catch (error) {
    if (context.mounted && dialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
    }
    if (context.mounted) showMessage(context, 'Export failed: $error');
  } finally {
    await ChronicleNarrationService.deleteFiles(narrationPaths);
  }
}
""" + main[end:]

    main = replace_once(
        main,
        "              title: topic.trim().isEmpty ? 'Chronicle History' : topic.trim(),\n"
        "              sceneTitles: buildSceneTitles(topic, 4),",
        "              title: topic.trim().isEmpty ? 'Chronicle History' : topic.trim(),\n"
        "              voice: voice,\n"
        "              sceneTitles: buildSceneTitles(topic, 4),",
        "Automatic generator voice",
    )

    main = replace_once(
        main,
        "              title: widget.projectTitle,\n"
        "              sceneTitles: buildSceneTitles(",
        "              title: widget.projectTitle,\n"
        "              voice: voice,\n"
        "              sceneTitles: buildSceneTitles(",
        "Editor voice",
    )

    exporter = replace_once(
        exporter,
        "    int? totalDurationSeconds,\n  }) async {",
        "    int? totalDurationSeconds,\n"
        "    required List<String> narrationAudioPaths,\n  }) async {",
        "Exporter narration parameter",
    )

    exporter = replace_once(
        exporter,
        "    if (sceneTitles.isEmpty) {\n"
        "      throw ArgumentError('At least one scene is required.');\n"
        "    }",
        "    if (sceneTitles.isEmpty) {\n"
        "      throw ArgumentError('At least one scene is required.');\n"
        "    }\n"
        "    if (narrationAudioPaths.length != sceneTitles.length) {\n"
        "      throw ArgumentError('Each scene needs narration audio.');\n"
        "    }",
        "Narration validation",
    )

    exporter = replace_once(
        exporter,
        "          sceneTitle: sceneTitles[index],\n"
        "          sceneNumber: index + 1,",
        "          sceneTitle: sceneTitles[index],\n"
        "          subtitleText: sceneTitles[index],\n"
        "          sceneNumber: index + 1,",
        "Subtitle argument",
    )

    exporter = replace_once(
        exporter,
        "    required String sceneTitle,\n"
        "    required int sceneNumber,",
        "    required String sceneTitle,\n"
        "    required String subtitleText,\n"
        "    required int sceneNumber,",
        "Subtitle parameter",
    )

    exporter = replace_once(
        exporter,
        "    drawText(\n      projectTitle,",
        """    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(52, 845, 616, 150),
        const Radius.circular(18),
      ),
      Paint()..color = const Color(0xE6090B0C),
    );
    drawText(
      subtitleText,
      870,
      25,
      Colors.white,
      weight: FontWeight.w600,
      maxLines: 3,
      maxWidth: 555,
    );
    drawText(
      projectTitle,""",
        "Subtitle drawing",
    )

    a = exporter.find("      final command =")
    b = exporter.find("      final session = await FFmpegKit.execute(command);", a)
    if a < 0 or b < 0:
        raise ValueError("Could not locate FFmpeg command.")

    command = r"""      final narrationInputs =
          narrationAudioPaths.map((p) => "-i '$p' ").join();
      final filters = <String>[];

      for (var i = 0; i < narrationAudioPaths.length; i++) {
        filters.add(
          '[${i + 1}:a]apad=pad_dur=$secondsPerScene,'
          'atrim=duration=$secondsPerScene,'
          'asetpts=PTS-STARTPTS[n$i]',
        );
      }

      final labels = List.generate(
        narrationAudioPaths.length, (i) => '[n$i]',
      ).join();
      final ambientIndex = narrationAudioPaths.length + 1;
      filters.add('$labels'
          'concat=n=${narrationAudioPaths.length}:v=0:a=1[narration]');
      filters.add('[$ambientIndex:a]volume=0.20[music]');
      filters.add('[narration][music]'
          'amix=inputs=2:duration=longest:normalize=0[aout]');

      final filterComplex = filters.join(';');
      final command =
          "-y "
          "-f concat -safe 0 -i '${concatFile.path}' "
          "$narrationInputs"
          "-i '${ambientAudio.path}' "
          '-filter_complex "$filterComplex" '
          '-map 0:v:0 -map "[aout]" '
          '-vf "$filter" '
          '-c:v mpeg4 -q:v 5 -r $framesPerSecond '
          '-c:a aac -b:a 128k -t $totalSeconds '
          '-shortest -movflags +faststart '
          "'${output.path}'";

"""
    exporter = exporter[:a] + command + exporter[b:]

    backup = root / "backups" / (
        "pre_narration_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    backup.mkdir(parents=True, exist_ok=False)
    for p in paths:
        shutil.copy2(p, backup / p.name)

    service_path.write_text(service)
    main_path.write_text(main)
    exporter_path.write_text(exporter)
    manifest_path.write_text(manifest)
    pubspec_path.write_text(pubspec)

    print("PATCH_APPLIED")
    print("Backup:", backup)

except Exception as e:
    sys.exit(f"STOP: {e}. No project source files were written.")
