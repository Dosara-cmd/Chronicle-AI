from pathlib import Path

path = Path("lib/main.dart")
source = path.read_text()

def replace_once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stopped safely: expected one match for {label}, found {count}. "
            "No changes have been written by this script."
        )
    source = source.replace(old, new, 1)
    print(f"Prepared: {label}")

# A local template, not a claim of AI research.
replace_once(
    "Future<void> renderAndShareVideo(",
    """String buildVideoDescription(String input) {
  final clean = input.trim().replaceAll(RegExp(r'\\s+'), ' ');
  final firstSentence = clean
      .split(RegExp(r'(?<=[.!?])\\s+'))
      .first
      .trim();
  final subject = firstSentence.isEmpty
      ? 'this fascinating story from history'
      : firstSentence;
  final shortSubject = subject.length > 120
      ? '${subject.substring(0, 117)}...'
      : subject;

  final isAfricanHistory = RegExp(
    r'\\b(Africa|African|Mali|Benin|Songhai|Ghana Empire|Great Zimbabwe|'
    r'Kush|Aksum|Ashanti|Yoruba|Zulu|Kongo|Oyo Empire)\\b',
    caseSensitive: false,
  ).hasMatch(clean);

  final hashtags = isAfricanHistory
      ? '#AfricanHistory #HistoryTok #ChronicleAI'
      : '#HistoryTok #History #ChronicleAI';

  return 'Discover the story behind $shortSubject '
      'and explore the people, events, and legacy that shaped history.\\n\\n'
      '$hashtags';
}

Future<void> renderAndShareVideo(""",
    "description suggestion helper",
)

replace_once(
    "  required List<String> sceneTitles,\n  required String duration,\n}) async {",
    "  required List<String> sceneTitles,\n"
    "  required String duration,\n"
    "  required String description,\n"
    "}) async {",
    "export function description parameter",
)

replace_once(
    "        text: 'Created with Chronicle AI',",
    "        text: description.trim().isEmpty\n"
    "            ? 'Created with Chronicle AI'\n"
    "            : '${description.trim()}\\n\\nCreated with Chronicle AI',",
    "share description with exported MP4",
)

# Automatic Generator: controller and cleanup.
replace_once(
    "  final topicController = TextEditingController();",
    "  final topicController = TextEditingController();\n"
    "  final descriptionController = TextEditingController();",
    "automatic generator description controller",
)
replace_once(
    "    topicController.dispose();\n    super.dispose();",
    "    topicController.dispose();\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();",
    "automatic generator controller cleanup",
)

# Insert an editable caption and suggestion button in Automatic Generator.
replace_once(
    "          const SizedBox(height: 24),\n"
    "          const FieldLabel('VIDEO DURATION'),",
    """          const SizedBox(height: 22),
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
          const FieldLabel('VIDEO DURATION'),""",
    "automatic generator description field",
)

# Paste Generator: controller and cleanup.
replace_once(
    "  final scriptController = TextEditingController();",
    "  final scriptController = TextEditingController();\n"
    "  final descriptionController = TextEditingController();",
    "paste generator description controller",
)
replace_once(
    "    scriptController.dispose();\n    super.dispose();",
    "    scriptController.dispose();\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();",
    "paste generator controller cleanup",
)

replace_once(
    "          const SizedBox(height: 24),\n"
    "          const FieldLabel('VIDEO DURATION'),",
    """          const SizedBox(height: 22),
          const FieldLabel('VIDEO DESCRIPTION'),
          TextField(
            controller: descriptionController,
            minLines: 2,
            maxLines: 4,
            maxLength: 300,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText: 'Write a short caption for your historical video...',
              alignLabelWithHint: true,
            ),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: () {
                final input = scriptController.text.trim();
                if (input.isEmpty) {
                  showMessage(context, 'Paste your script first.');
                  return;
                }
                descriptionController.text = buildVideoDescription(input);
              },
              icon: const Icon(Icons.auto_awesome, size: 18),
              label: const Text('Suggest description'),
            ),
          ),
          const SizedBox(height: 12),
          const FieldLabel('VIDEO DURATION'),""",
    "paste generator description field",
)

# Pass captions into PreparationScreen from both generators.
replace_once(
    "                    topic: topicController.text.trim(),\n"
    "                    style: style,\n"
    "                    voice: voice,\n"
    "                    duration: duration,",
    "                    topic: topicController.text.trim(),\n"
    "                    style: style,\n"
    "                    voice: voice,\n"
    "                    duration: duration,\n"
    "                    description: descriptionController.text.trim().isEmpty\n"
    "                        ? buildVideoDescription(topicController.text.trim())\n"
    "                        : descriptionController.text.trim(),",
    "automatic generator caption handoff",
)
replace_once(
    "                    topic: script,\n"
    "                    style: style,\n"
    "                    voice: voice,\n"
    "                    duration: duration,",
    "                    topic: script,\n"
    "                    style: style,\n"
    "                    voice: voice,\n"
    "                    duration: duration,\n"
    "                    description: descriptionController.text.trim().isEmpty\n"
    "                        ? buildVideoDescription(script)\n"
    "                        : descriptionController.text.trim(),",
    "paste generator caption handoff",
)

# PreparationScreen receives the description and forwards it.
replace_once(
    "    this.pastedScript = false,\n  });",
    "    this.pastedScript = false,\n"
    "    this.description = '',\n"
    "  });",
    "preparation screen description argument",
)
replace_once(
    "  final bool pastedScript;\n",
    "  final bool pastedScript;\n"
    "  final String description;\n",
    "preparation screen description property",
)
replace_once(
    "                  selectedVoice: voice,\n"
    "                duration: duration,",
    "                  selectedVoice: voice,\n"
    "                  duration: duration,\n"
    "                  description: description,",
    "preparation-to-editor description handoff",
)
replace_once(
    "              sceneTitles: buildSceneTitles(topic, 4),\n"
    "              duration: duration,",
    "              sceneTitles: buildSceneTitles(topic, 4),\n"
    "              duration: duration,\n"
    "              description: description,",
    "preparation export description",
)

# Editing Studio: store and dispose an editable caption controller.
replace_once(
    "    this.selectedVoice = 'Deep Documentary',\n"
    "  this.duration = '3 minutes',\n"
    "  });",
    "    this.selectedVoice = 'Deep Documentary',\n"
    "    this.duration = '3 minutes',\n"
    "    this.description = '',\n"
    "  });",
    "editor description argument",
)
replace_once(
    "  final String duration;\n"
    "@override\n"
    "  State<EditorScreen> createState() => _EditorScreenState();",
    "  final String duration;\n"
    "  final String description;\n"
    "  @override\n"
    "  State<EditorScreen> createState() => _EditorScreenState();",
    "editor description property",
)
replace_once(
    "  String activeTool = 'Scenes';\n",
    "  String activeTool = 'Scenes';\n"
    "  late final TextEditingController descriptionController;\n",
    "editor description controller",
)
replace_once(
    "    style = widget.selectedStyle;\n"
    "    voice = widget.selectedVoice;\n"
    "  }",
    "    style = widget.selectedStyle;\n"
    "    voice = widget.selectedVoice;\n"
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
    "initialize editor description",
)

# Add the Description tool to the editor toolbar.
replace_once(
    "                  'Transitions',                                  'Style',",
    "                  'Transitions',                                  'Style',\n"
    "                  'Description',",
    "editor description tool button",
)

# Add a working text editor panel for the description.
replace_once(
    "      case 'Scenes':\n",
    """      case 'Description':
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
              'This text is included when you share the exported video.',
              style: TextStyle(color: muted, fontSize: 12, height: 1.5),
            ),
          ],
        );
      case 'Scenes':
""",
    "editor description panel",
)

# Export the caption currently shown in the Editing Studio.
replace_once(
    "              duration: widget.duration,",
    "              duration: widget.duration,\n"
    "              description: descriptionController.text.trim(),",
    "editor export description",
)

# Release the controller when the Editing Studio closes.
replace_once(
    "  @override\n  Widget build(BuildContext context) {\n"
    "    return PageFrame(\n      title: 'Editing studio',",
    "  @override\n  void dispose() {\n"
    "    descriptionController.dispose();\n"
    "    super.dispose();\n"
    "  }\n\n"
    "  @override\n  Widget build(BuildContext context) {\n"
    "    return PageFrame(\n      title: 'Editing studio',",
    "editor description controller cleanup",
)

path.write_text(source)
print("\nDescription feature changes written to lib/main.dart.")
