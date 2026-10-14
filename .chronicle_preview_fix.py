from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
main_path = root / "lib/main.dart"
pubspec_path = root / "pubspec.yaml"

main = main_path.read_text()
pubspec = pubspec_path.read_text()

if "class ChronicleVideoPreviewScreen" in main:
    print("Preview screen already exists. No duplicate changes made.")
    raise SystemExit(0)

# Locate the actual preview container and export/share flow.
preview_start = main.find(
    "          Container(\n"
    "            width: double.infinity,\n"
    "            height: 390,"
)
preview_end = main.find(
    "          const SizedBox(height: 20),\n"
    "          Row(",
    preview_start,
)

share_start = main.find(
    "    await SharePlus.instance.share(ShareParams("
)
share_end_marker = (
    "if (context.mounted) showMessage(context, 'Video exported: ${file.path}');"
)
share_end = main.find(share_end_marker, share_start)

if preview_start < 0 or preview_end < 0:
    raise SystemExit(
        "STOPPED: Could not locate the exact editor preview container. "
        "No source files changed."
    )

if share_start < 0 or share_end < 0:
    raise SystemExit(
        "STOPPED: Could not locate the export/share section. "
        "No source files changed."
    )

if "import 'package:flutter/material.dart';" not in main:
    raise SystemExit("STOPPED: Flutter import not found.")

if "flutter_tts: ^4.2.5" not in pubspec:
    raise SystemExit("STOPPED: Expected flutter_tts dependency not found.")

backup = root / "backups" / (
    "pre_real_preview_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_path, backup / "main.dart")
shutil.copy2(pubspec_path, backup / "pubspec.yaml")

# Required imports.
if "import 'dart:io';" not in main:
    main = "import 'dart:io';\n" + main

if "package:video_player/video_player.dart" not in main:
    main = main.replace(
        "import 'package:flutter/material.dart';",
        "import 'package:flutter/material.dart';\n"
        "import 'package:video_player/video_player.dart';",
        1,
    )

# Replace the static preview with a connected generation action.
preview_start = main.find(
    "          Container(\n"
    "            width: double.infinity,\n"
    "            height: 390,"
)
preview_end = main.find(
    "          const SizedBox(height: 20),\n"
    "          Row(",
    preview_start,
)

new_preview = """          ChronicleEditorPreview(
            onGenerate: () => renderAndShareVideo(
              context,
              title: widget.projectTitle,
              sceneTitles: buildSceneTitles(
                widget.projectInput.isNotEmpty
                    ? widget.projectInput
                    : widget.projectTitle,
                sceneCount,
              ),
              duration: widget.duration,
              description: descriptionController.text,
              voice: voice,
            ),
          ),
"""

main = main[:preview_start] + new_preview + main[preview_end:]

# After successful rendering, navigate to the actual MP4 preview.
share_start = main.find(
    "    await SharePlus.instance.share(ShareParams("
)
share_end = main.find(share_end_marker, share_start) + len(share_end_marker)

new_flow = """    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ChronicleVideoPreviewScreen(
          file: file,
          title: title,
          description: description,
        ),
      ),
    );"""

main = main[:share_start] + new_flow + main[share_end:]

# Clarify what the current renderer really produces.
main = main.replace(
    "This preview confirms your project settings. "
    "It does not generate an AI video yet.",
    "Chronicle AI renders animated illustrated historical scenes. "
    "Realistic AI-generated historical footage is not available yet.",
    1,
)

# Add the real preview and playback screen.
marker = "class PreparationScreen extends StatelessWidget {"
if marker not in main:
    raise SystemExit("STOPPED: PreparationScreen marker not found.")

classes = r'''
class ChronicleEditorPreview extends StatelessWidget {
  const ChronicleEditorPreview({super.key, required this.onGenerate});

  final VoidCallback onGenerate;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: const Color(0xFF202124),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: gold.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          const Icon(Icons.movie_creation_outlined, color: gold, size: 54),
          const SizedBox(height: 14),
          const Text(
            'VIDEO PREVIEW',
            style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 2),
          ),
          const SizedBox(height: 8),
          const Text(
            '9:16 vertical video',
            style: TextStyle(color: muted, fontSize: 12),
          ),
          const SizedBox(height: 12),
          const Text(
            'Generate your video to open the playable MP4 preview.',
            textAlign: TextAlign.center,
            style: TextStyle(color: muted, fontSize: 13, height: 1.5),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onGenerate,
              icon: const Icon(Icons.play_circle_outline),
              label: const Text('Generate and preview video'),
              style: OutlinedButton.styleFrom(
                foregroundColor: gold,
                side: const BorderSide(color: gold),
                minimumSize: const Size.fromHeight(48),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ChronicleVideoPreviewScreen extends StatefulWidget {
  const ChronicleVideoPreviewScreen({
    super.key,
    required this.file,
    required this.title,
    required this.description,
  });

  final File file;
  final String title;
  final String description;

  @override
  State<ChronicleVideoPreviewScreen> createState() =>
      _ChronicleVideoPreviewScreenState();
}

class _ChronicleVideoPreviewScreenState
    extends State<ChronicleVideoPreviewScreen> {
  late final VideoPlayerController _controller;
  String? _error;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.file(widget.file);
    _controller.addListener(_videoChanged);
    _initializeVideo();
  }

  void _videoChanged() {
    if (mounted) setState(() {});
  }

  Future<void> _initializeVideo() async {
    try {
      await _controller.initialize();
      await _controller.setLooping(true);
      if (mounted) setState(() {});
    } catch (error) {
      if (mounted) {
        setState(() => _error = 'Unable to play this MP4: $error');
      }
    }
  }

  @override
  void dispose() {
    _controller.removeListener(_videoChanged);
    _controller.dispose();
    super.dispose();
  }

  Future<void> _shareVideo() async {
    await SharePlus.instance.share(
      ShareParams(
        files: [XFile(widget.file.path)],
        text: widget.description.trim().isEmpty
            ? 'Created with Chronicle AI'
            : '${widget.description.trim()}\n\nCreated with Chronicle AI',
        subject: widget.title,
      ),
    );
  }

  String _time(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    final ready = _controller.value.isInitialized;

    return Scaffold(
      backgroundColor: bg,
      appBar: AppBar(
        backgroundColor: bg,
        foregroundColor: Colors.white,
        title: const Text('Video preview'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              widget.title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: gold.withValues(alpha: 0.35)),
              ),
              child: _error != null
                  ? Padding(
                      padding: const EdgeInsets.all(20),
                      child: Text(
                        _error!,
                        style: const TextStyle(color: Colors.white),
                      ),
                    )
                  : !ready
                      ? const SizedBox(
                          height: 280,
                          child: Center(
                            child: CircularProgressIndicator(color: gold),
                          ),
                        )
                      : Column(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: AspectRatio(
                                aspectRatio: _controller.value.aspectRatio,
                                child: VideoPlayer(_controller),
                              ),
                            ),
                            Row(
                              children: [
                                IconButton(
                                  tooltip: _controller.value.isPlaying
                                      ? 'Pause video'
                                      : 'Play video',
                                  color: gold,
                                  onPressed: () async {
                                    if (_controller.value.isPlaying) {
                                      await _controller.pause();
                                    } else {
                                      await _controller.play();
                                    }
                                  },
                                  icon: Icon(
                                    _controller.value.isPlaying
                                        ? Icons.pause_circle_filled
                                        : Icons.play_circle_fill,
                                    size: 38,
                                  ),
                                ),
                                Expanded(
                                  child: VideoProgressIndicator(
                                    _controller,
                                    allowScrubbing: true,
                                    colors: const VideoProgressColors(
                                      playedColor: gold,
                                      bufferedColor: muted,
                                      backgroundColor: surface2,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '${_time(_controller.value.position)} / '
                                  '${_time(_controller.value.duration)}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: _shareVideo,
              icon: const Icon(Icons.share),
              label: const Text('Share MP4 video'),
              style: FilledButton.styleFrom(
                backgroundColor: gold,
                foregroundColor: bg,
                minimumSize: const Size.fromHeight(52),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Saved video: ${widget.file.path}',
              style: const TextStyle(color: muted, fontSize: 11),
            ),
          ],
        ),
      ),
    );
  }
}

'''

main = main.replace(marker, classes + marker, 1)

# Add the video player dependency.
if "video_player:" not in pubspec:
    pubspec = pubspec.replace(
        "  flutter_tts: ^4.2.5",
        "  flutter_tts: ^4.2.5\n  video_player: ^2.10.0",
        1,
    )

# Write both files only after all checks and transformations succeed.
main_path.write_text(main)
pubspec_path.write_text(pubspec)

print("PATCH_APPLIED")
print(f"Backup: {backup}")
print("Added a real MP4 preview screen with playback, scrubbing, and sharing.")
