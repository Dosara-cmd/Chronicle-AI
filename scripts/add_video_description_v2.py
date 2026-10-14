from pathlib import Path
import re
from datetime import datetime

path = Path("lib/main.dart")
source = path.read_text()

def replace_once(text, pattern, replacement, label, flags=0):
    def safe_replacement(match):
        result = replacement
        if r"\1" in result:
            result = result.replace(r"\1", match.group(1))
            result = result.replace(r"\n", "\n")
        return result

    updated, count = re.subn(
        pattern, safe_replacement, text, count=1, flags=flags
    )
    if count != 1:
        raise RuntimeError(
            f"Stopped safely: {label}: expected one match, found {count}. "
            "The app source has not been written."
        )
    print(f"Prepared: {label}")
    return updated

def replace_in_region(text, start_marker, end_marker, pattern, replacement, label, flags=0):
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"Missing start marker for {label}. No app changes written.")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise RuntimeError(f"Missing end marker for {label}. No app changes written.")

    region = text[start:end]
    updated = replace_once(region, pattern, replacement, label, flags)
    return text[:start] + updated + text[end:]

# 1. Local caption suggestion helper.
source = replace_once(
    source,
    r"Future<void> renderAndShareVideo\(",
    r"""String buildVideoDescription(String input) {
  final clean = input.trim().replaceAll(RegExp(r'\s+'), ' ');
  final firstSentence = clean
      .split(RegExp(r'(?<=[.!?])\s+'))
      .first
      .trim();
  final subject = firstSentence.isEmpty
      ? 'this fascinating story from history'
      : firstSentence;
  final shortSubject = subject.length > 120
      ? '${subject.substring(0, 117)}...'
      : subject;

  final isAfricanHistory = RegExp(
    r'\b(Africa|African|Mali|Benin|Songhai|Ghana Empire|Great Zimbabwe|'
    r'Kush|Aksum|Ashanti|Yoruba|Zulu|Kongo|Oyo Empire)\b',
    caseSensitive: false,
  ).hasMatch(clean);

  final hashtags = isAfricanHistory
      ? '#AfricanHistory #HistoryTok #ChronicleAI'
      : '#HistoryTok #History #ChronicleAI';

  return 'Explore the fascinating story of "$shortSubject" and discover '
      'the people, events, and legacy that shaped history.\n\n$hashtags';
}

Future<void> renderAndShareVideo(""",
    "caption suggestion helper",
)

# 2. Pass a description into the existing export/share function.
source = replace_once(
    source,
    r"required List<String> sceneTitles,\s*required String duration,\s*\}\) async \{",
    "required List<String> sceneTitles,\n"
    "  required String duration,\n"
    "  required String description,\n"
    "}) async {",
    "export function description parameter",
)

source = replace_once(
    source,
    r"text: 'Created with Chronicle AI',",
    "text: description.trim().isEmpty\n"
    "            ? 'Created with Chronicle AI'\n"
    "            : '${description.trim()}\\n\\nCreated with Chronicle AI',",
    "share caption alongside exported MP4",
)

# 3. Automatic Generator: controller, UI, and preparation handoff.
source = replace_in_region(
    source,
    "class _AutomaticGeneratorScreenState",
    "class PasteGeneratorScreen",
    r"final topicController = TextEditingController\(\);",
    "final topicController = TextEditingController();\n"
    "  final descriptionController = TextEditingController();",
    "automatic generator caption controller",
)

source = replace_in_region(
    source,
    "class _AutomaticGeneratorScreenState",
    "class PasteGeneratorScreen",
    r"topicController\.dispose\(\);\s*super\.dispose\(\);",
    "topicController.dispose();\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();",
    "automatic generator controller cleanup",
)

caption_field = """          const SizedBox(height: 22),
          const FieldLabel('VIDEO DESCRIPTION'),
          TextField(
            controller: descriptionController,
            minLines: 2,
            maxLines: 4,
            maxLength: 300,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText: 'Write a short caption for TikTok or other platforms...',
              alignLabelWithHint: true,
            ),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: () {
                final input = topicController.text.trim();
                if (input.isEmpty) {
                  showMessage(context, 'Enter a topic first.');
                  return;
                }
                descriptionController.text = buildVideoDescription(input);
              },
              icon: const Icon(Icons.auto_awesome, size: 18),
              label: const Text('Suggest description'),
            ),
          ),
          const SizedBox(height: 12),
"""

source = replace_in_region(
    source,
    "class _AutomaticGeneratorScreenState",
    "class PasteGeneratorScreen",
    r"          const SizedBox\(height: 24\),\s*const FieldLabel\('VIDEO DURATION'\),",
    caption_field + "          const FieldLabel('VIDEO DURATION'),",
    "automatic generator caption field",
)

source = replace_in_region(
    source,
    "class _AutomaticGeneratorScreenState",
    "class PasteGeneratorScreen",
    r"(topic: topicController\.text\.trim\(\),.*?duration: duration,)",
    r"\1\n                    description: descriptionController.text.trim().isEmpty\n"
    r"                        ? buildVideoDescription(topicController.text.trim())\n"
    r"                        : descriptionController.text.trim(),",
    "automatic generator caption handoff",
    re.S,
)

# 4. Paste Generator: controller, UI, and preparation handoff.
source = replace_in_region(
    source,
    "class _PasteGeneratorScreenState",
    "List<String> buildSceneTitles",
    r"final scriptController = TextEditingController\(\);",
    "final scriptController = TextEditingController();\n"
    "  final descriptionController = TextEditingController();",
    "paste generator caption controller",
)

source = replace_in_region(
    source,
    "class _PasteGeneratorScreenState",
    "List<String> buildSceneTitles",
    r"scriptController\.dispose\(\);\s*super\.dispose\(\);",
    "scriptController.dispose();\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();",
    "paste generator controller cleanup",
)

paste_caption_field = caption_field.replace(
    "topicController",
    "scriptController",
).replace(
    "Enter a topic first.",
    "Paste your script first.",
)

source = replace_in_region(
    source,
    "class _PasteGeneratorScreenState",
    "List<String> buildSceneTitles",
    r"          const SizedBox\(height: 24\),\s*const FieldLabel\('VIDEO DURATION'\),",
    paste_caption_field + "          const FieldLabel('VIDEO DURATION'),",
    "paste generator caption field",
)

source = replace_in_region(
    source,
    "class _PasteGeneratorScreenState",
    "List<String> buildSceneTitles",
    r"(topic: script,.*?duration: duration,)",
    r"\1\n                    description: descriptionController.text.trim().isEmpty\n"
    r"                        ? buildVideoDescription(script)\n"
    r"                        : descriptionController.text.trim(),",
    "paste generator caption handoff",
    re.S,
)

# 5. Preparation Screen: receive and forward the description.
source = replace_in_region(
    source,
    "class PreparationScreen extends StatelessWidget",
    "const List<String> videoStyles",
    r"this\.pastedScript = false,\s*\}\);",
    "this.pastedScript = false,\n    this.description = '',\n  });",
    "preparation screen description argument",
)

source = replace_in_region(
    source,
    "class PreparationScreen extends StatelessWidget",
    "const List<String> videoStyles",
    r"final bool pastedScript;",
    "final bool pastedScript;\n  final String description;",
    "preparation screen description property",
)

source = replace_in_region(
    source,
    "class PreparationScreen extends StatelessWidget",
    "const List<String> videoStyles",
    r"(selectedVoice: voice,\s*duration: duration,)",
    r"\1\n                  description: description,",
    "preparation-to-editor caption handoff",
)

source = replace_in_region(
    source,
    "class PreparationScreen extends StatelessWidget",
    "const List<String> videoStyles",
    r"(sceneTitles: buildSceneTitles\(topic, 4\),\s*duration: duration,)",
    r"\1\n              description: description,",
    "preparation export caption",
)

# 6. Editing Studio: receive, edit, and export the caption.
source = replace_in_region(
    source,
    "class EditorScreen extends StatefulWidget",
    "class ProjectsScreen",
    r"this\.duration = '3 minutes',\s*\}\);",
    "this.duration = '3 minutes',\n    this.description = '',\n  });",
    "editor description argument",
)

source = replace_in_region(
    source,
    "class EditorScreen extends StatefulWidget",
    "class ProjectsScreen",
    r"final String duration;",
    "final String duration;\n  final String description;",
    "editor description property",
)

source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"String activeTool = 'Scenes';",
    "String activeTool = 'Scenes';\n"
    "  late final TextEditingController descriptionController;",
    "editor caption controller",
)

source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"(style = widget\.selectedStyle;\s*voice = widget\.selectedVoice;)\s*\}",
    r"\1\n"
    "    descriptionController = TextEditingController(\n"
    "      text: widget.description.trim().isNotEmpty\n"
    "          ? widget.description\n"
    "          : buildVideoDescription(\n"
    "              widget.projectInput.isNotEmpty\n"
    "                  ? widget.projectInput\n"
    "                  : widget.projectTitle,\n"
    "            ),\n"
    "    );\n"
    "  }",
    "initialize editor caption",
)

source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"('Transitions',\s*'Style',)",
    r"\1\n                  'Description',",
    "editor description tool button",
)

description_panel = """      case 'Description':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Video description / social caption',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: descriptionController,
              minLines: 3,
              maxLines: 6,
              maxLength: 300,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                hintText: 'Add a caption and hashtags...',
                alignLabelWithHint: true,
              ),
            ),
            const Text(
              'This caption is included when you share the exported video.',
              style: TextStyle(color: muted, fontSize: 12, height: 1.5),
            ),
          ],
        );
      case 'Scenes':
"""

source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"case 'Scenes':",
    description_panel,
    "editor caption editing panel",
)

source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"duration: widget\.duration,",
    "duration: widget.duration,\n"
    "              description: descriptionController.text.trim(),",
    "editor export caption",
)

# Add proper controller disposal before the editor's build method.
source = replace_in_region(
    source,
    "class _EditorScreenState",
    "class ProjectsScreen",
    r"(@override\s+Widget build\(BuildContext context\)\s*\{\s*return PageFrame\(\s*title: 'Editing studio',)",
    "  @override\n"
    "  void dispose() {\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();\n"
    "  }\n\n"
    r"\1",
    "editor caption controller disposal",
)

# All edits were prepared and validated in memory. Only now write the file.
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"main.dart.before_description_v2_{datetime.now():%Y%m%d_%H%M%S}.dart"
backup.write_text(Path("lib/main.dart").read_text())
path.write_text(source)

print(f"\nBackup saved: {backup}")
print("Description feature patch written to lib/main.dart.")
