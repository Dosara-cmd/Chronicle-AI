from pathlib import Path
import shutil
import sys

root = Path.cwd()
main_path = root / "lib/main.dart"
pubspec_path = root / "pubspec.yaml"

if not main_path.is_file() or not pubspec_path.is_file():
    sys.exit("ERROR: Run this script from ~/chronicle_ai.")

main = main_path.read_text()
pubspec = pubspec_path.read_text()

original = main

# Add imports.
import_anchor = "import 'package:flutter/material.dart';"
required_imports = [
    "import 'package:cross_file/cross_file.dart';",
    "import 'package:share_plus/share_plus.dart';",
    "import 'services/video_exporter.dart';",
]

if import_anchor not in main:
    sys.exit("ERROR: Could not find the Flutter material import.")

for item in required_imports:
    if item not in main:
        main = main.replace(
            import_anchor,
            import_anchor + "\n" + item,
            1,
        )
        import_anchor = item

# Make cross_file a direct dependency because the app uses XFile.
if "  cross_file:" not in pubspec:
    anchor = "  share_plus: ^12.0.1"
    if anchor not in pubspec:
        sys.exit("ERROR: Could not find the share_plus dependency.")
    pubspec = pubspec.replace(
        anchor,
        anchor + "\n  cross_file: ^0.3.5+5",
        1,
    )

# Preserve the user's actual topic or pasted script in the editor.
editor_constructor = """class EditorScreen extends StatefulWidget {
  const EditorScreen({
    super.key,
    this.projectTitle = 'Untitled history video',
    this.selectedStyle = 'Cinematic Realism',
    this.selectedVoice = 'Deep Documentary',
  });

  final String projectTitle;
  final String selectedStyle;
  final String selectedVoice;
"""

editor_constructor_new = """class EditorScreen extends StatefulWidget {
  const EditorScreen({
    super.key,
    this.projectTitle = 'Untitled history video',
    this.projectInput = '',
    this.selectedStyle = 'Cinematic Realism',
    this.selectedVoice = 'Deep Documentary',
  });

  final String projectTitle;
  final String projectInput;
  final String selectedStyle;
  final String selectedVoice;
"""

if editor_constructor in main:
    main = main.replace(editor_constructor, editor_constructor_new, 1)
elif "final String projectInput;" not in main:
    sys.exit("ERROR: EditorScreen constructor did not match expected code.")

# Add a scene-title helper and the shared render/share workflow.
helper_anchor = "class PreparationScreen extends StatelessWidget {"

helper = r'''
List<String> buildSceneTitles(String input, int sceneCount) {
  final cleanInput = input.trim();
  final count = sceneCount.clamp(1, 20);

  if (cleanInput.isEmpty) {
    return List.generate(
      count,
      (index) => 'Historical chapter ${index + 1}',
    );
  }

  // Split pasted scripts into sentences or paragraphs when possible.
  final parts = cleanInput
      .split(RegExp(r'(?<=[.!?])\s+|\n+'))
      .map((part) => part.trim())
      .where((part) => part.isNotEmpty)
      .toList();

  if (parts.length >= count) {
    return List.generate(count, (index) => parts[index]);
  }

  // For a short topic, create clear title-card chapter headings.
  if (parts.length <= 1) {
    final topic = cleanInput.length > 110
        ? '${cleanInput.substring(0, 107)}...'
        : cleanInput;

    const chapterNames = [
      'The world before',
      'The origins and rise of',
      'A turning point in',
      'The legacy of',
      'The people behind',
      'The lasting impact of',
      'The historical significance of',
      'Lessons from',
    ];

    return List.generate(count, (index) {
      final chapter = chapterNames[index % chapterNames.length];
      return '$chapter $topic';
    });
  }

  // Combine short scripts into the requested number of scenes.
  return List.generate(count, (index) {
    final start = index * parts.length ~/ count;
    var end = (index + 1) * parts.length ~/ count;

    if (end <= start) end = start + 1;
    if (end > parts.length) end = parts.length;

    return parts.sublist(start, end).join(' ');
  });
}

Future<void> renderAndShareVideo(
  BuildContext context, {
  required String title,
  required List<String> sceneTitles,
}) async {
  var progressDialogOpen = false;

  try {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => const AlertDialog(
        backgroundColor: surface2,
        content: Row(
          children: [
            SizedBox(
              width: 26,
              height: 26,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                color: gold,
              ),
            ),
            SizedBox(width: 18),
            Expanded(
              child: Text(
                'Rendering your vertical video. '
                'This may take a while on your phone.',
              ),
            ),
          ],
        ),
      ),
    );
    progressDialogOpen = true;

    final file = await ChronicleVideoExporter.exportTitleCardVideo(
      title: title,
      sceneTitles: sceneTitles,
      secondsPerScene: 30,
    );

    if (context.mounted && progressDialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
      progressDialogOpen = false;
    }

    if (!context.mounted) return;

    await SharePlus.instance.share(
      ShareParams(
        files: [XFile(file.path)],
        text: 'Created with Chronicle AI',
        subject: title,
      ),
    );

    if (context.mounted) {
      showMessage(context, 'Video exported: ${file.path}');
    }
  } catch (error) {
    if (context.mounted && progressDialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
      progressDialogOpen = false;
    }

    if (context.mounted) {
      showMessage(
        context,
        'Video export failed. Please try again. Details: $error',
      );
    }
  }
}

'''

if helper_anchor not in main:
    sys.exit("ERROR: Could not find PreparationScreen insertion point.")

if "Future<void> renderAndShareVideo(" not in main:
    main = main.replace(helper_anchor, helper + helper_anchor, 1)

# Replace the placeholder Generate video callback.
generate_old = """          OutlinedButton.icon(
            onPressed: () => showMessage(
              context,
              'The AI generation engine has not been connected yet.',
            ),
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Generate video'),
"""

generate_new = """          OutlinedButton.icon(
            onPressed: () => renderAndShareVideo(
              context,
              title: topic.trim().isEmpty ? 'Chronicle History' : topic.trim(),
              sceneTitles: buildSceneTitles(topic, 4),
            ),
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Generate video'),
"""

if generate_old in main:
    main = main.replace(generate_old, generate_new, 1)
elif "'The AI generation engine has not been connected yet.'" in main:
    sys.exit("ERROR: Generate button differed from the expected code.")
elif "sceneTitles: buildSceneTitles(topic, 4)" not in main:
    sys.exit("ERROR: Could not verify the Generate video integration.")

# Pass the actual input into the Editing Studio.
editor_call_old = """                builder: (_) => EditorScreen(
                  projectTitle: pastedScript ? 'Pasted script' : topic,
                  selectedStyle: style,
                  selectedVoice: voice,
                ),
"""

editor_call_new = """                builder: (_) => EditorScreen(
                  projectTitle: pastedScript ? 'Pasted script' : topic,
                  projectInput: topic,
                  selectedStyle: style,
                  selectedVoice: voice,
                ),
"""

if editor_call_old in main:
    main = main.replace(editor_call_old, editor_call_new, 1)
elif "projectInput: topic," not in main:
    sys.exit("ERROR: Could not connect the original input to the editor.")

# Replace the placeholder Export MP4 button.
export_old = """          PrimaryButton(
            label: 'Export MP4',
            icon: Icons.download_rounded,
            onPressed: () => showMessage(
              context,
              'Video rendering and MP4 export must be implemented '
              'before a file can be exported.',
            ),
          ),
"""

export_new = """          PrimaryButton(
            label: 'Export MP4',
            icon: Icons.download_rounded,
            onPressed: () => renderAndShareVideo(
              context,
              title: widget.projectTitle,
              sceneTitles: buildSceneTitles(
                widget.projectInput.isNotEmpty
                    ? widget.projectInput
                    : widget.projectTitle,
                sceneCount,
              ),
            ),
          ),
"""

if export_old in main:
    main = main.replace(export_old, export_new, 1)
elif "Video rendering and MP4 export must be implemented" in main:
    sys.exit("ERROR: Export button differed from the expected code.")
elif "sceneTitles: buildSceneTitles(" not in main:
    sys.exit("ERROR: Could not verify the Export MP4 integration.")

if main == original and pubspec == pubspec_path.read_text():
    print("No changes were necessary; the integration may already exist.")
else:
    backup = root / "backups/main.dart.before_video_integration"
    if not backup.exists():
        shutil.copy2(main_path, backup)
        print(f"Backup created: {backup.relative_to(root)}")

    main_path.write_text(main)
    pubspec_path.write_text(pubspec)
    print("Connected Generate video to the local renderer.")
    print("Connected Export MP4 to the local renderer.")
    print("Connected Android sharing for the exported MP4.")
    print("Preserved the input when opening the Editing Studio.")

print("\nPatch verification:")
updated = main_path.read_text()

for needle in (
    "Future<void> renderAndShareVideo(",
    "sceneTitles: buildSceneTitles(topic, 4)",
    "projectInput: topic",
    "label: 'Export MP4'",
):
    if needle not in updated:
        sys.exit(f"ERROR: Verification failed: {needle}")

print("All required integration markers are present.")
