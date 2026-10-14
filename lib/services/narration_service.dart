import 'dart:io';
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
