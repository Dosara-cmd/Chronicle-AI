import 'package:flutter/services.dart';

class VideoLibraryService {
  VideoLibraryService._();

  static const MethodChannel _channel = MethodChannel(
    'com.chronicleai.chronicle_ai/video_library',
  );

  static Future<String> saveVideo({
    required String sourcePath,
    required String displayName,
  }) async {
    final result = await _channel.invokeMethod<String>(
      'saveVideo',
      <String, String>{'sourcePath': sourcePath, 'displayName': displayName},
    );

    if (result == null || result.isEmpty) {
      throw Exception('Android did not return a saved-video location.');
    }

    return result;
  }
}
