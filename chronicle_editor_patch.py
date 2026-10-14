from pathlib import Path
import re
import sys
import shutil
from datetime import datetime

ROOT = Path.home() / "chronicle_ai"
main_path = ROOT / "lib/main.dart"
export_path = ROOT / "lib/services/video_exporter.dart"

main = main_path.read_text()
exporter = export_path.read_text()

def sub_once(text, pattern, replacement, label, flags=0):
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return updated

try:
    # Optional style argument preserves existing callers.
    main = sub_once(
        main,
        r"(Future<void>\s+renderAndShareVideo\(\s*BuildContext context,\s*\{\s*)required String title,",
        r"\1String style = 'Cinematic Realism',\n  required String title,",
        "generation function signature",
        re.S,
    )

    main = sub_once(
        main,
        r"(ChronicleVideoExporter\.exportTitleCardVideo\(\s*\n\s*title: title,)",
        r"\1\n      style: style,",
        "generation exporter call",
    )

    # Replace fixed scene count with editable scene data.
    main = sub_once(
        main,
        r"  int sceneCount = 4;\s*int selectedScene = 0;\s*String style = '';",
        """  int selectedScene = 0;
  String style = '';
  late List<String> sceneTitles;
  late final TextEditingController sceneTextController;""",
        "editor state",
    )

    main = sub_once(
        main,
        r"    style = widget\.selectedStyle;\s*voice = widget\.selectedVoice;\s*descriptionController = TextEditingController\(",
        """    style = widget.selectedStyle;
    voice = widget.selectedVoice;
    sceneTitles = buildSceneTitles(
      widget.projectInput.trim().isNotEmpty
          ? widget.projectInput
          : widget.projectTitle,
      4,
    );
    sceneTextController = TextEditingController(
      text: sceneTitles.first,
    );
    descriptionController = TextEditingController(""",
        "editor initialization",
    )

    main = sub_once(
        main,
        r"  void dispose\(\) \{\s*descriptionController\.dispose\(\);\s*super\.dispose\(\);\s*\}",
        """  void dispose() {
    descriptionController.dispose();
    sceneTextController.dispose();
    super.dispose();
  }

  void _saveSelectedSceneText() {
    if (sceneTitles.isEmpty ||
        selectedScene < 0 ||
        selectedScene >= sceneTitles.length) {
      return;
    }
    sceneTitles[selectedScene] = sceneTextController.text.trim();
  }

  void _selectScene(int index) {
    _saveSelectedSceneText();
    setState(() {
      selectedScene = index;
      sceneTextController.text = sceneTitles[index];
      sceneTextController.selection = TextSelection.collapsed(
        offset: sceneTextController.text.length,
      );
    });
  }

  void _addScene() {
    _saveSelectedSceneText();
    if (sceneTitles.length >= 20) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('A project can contain up to 20 scenes.'),
        ),
      );
      return;
    }
    setState(() {
      sceneTitles.add('New historical scene');
      selectedScene = sceneTitles.length - 1;
      sceneTextController.text = sceneTitles[selectedScene];
    });
  }

  void _moveSelectedScene(int direction) {
    _saveSelectedSceneText();
    final destination = selectedScene + direction;
    if (destination < 0 || destination >= sceneTitles.length) return;
    setState(() {
      final item = sceneTitles.removeAt(selectedScene);
      sceneTitles.insert(destination, item);
      selectedScene = destination;
      sceneTextController.text = sceneTitles[selectedScene];
    });
  }

  List<String> _currentSceneTitles() {
    _saveSelectedSceneText();
    return sceneTitles
        .map((scene) => scene.trim())
        .where((scene) => scene.isNotEmpty)
        .toList();
  }""",
        "editor methods",
    )

    # The preview must use the actual edited scene list.
    main = sub_once(
        main,
        r"sceneTitles:\s*buildSceneTitles\(\s*widget\.projectInput\.isNotEmpty\s*\?\s*widget\.projectInput\s*:\s*widget\.projectTitle,\s*sceneCount,\s*\),",
        "sceneTitles: _currentSceneTitles(),\n            style: style,",
        "editor preview scene list",
    )

    main = sub_once(
        main,
        r"onPressed:\s*\(\)\s*=>\s*setState\(\(\)\s*=>\s*sceneCount\+\+\),",
        "onPressed: _addScene,",
        "add scene action",
    )

    main = sub_once(
        main,
        r"itemCount:\s*sceneCount,",
        "itemCount: sceneTitles.length,",
        "timeline scene count",
    )

    main = sub_once(
        main,
        r"onTap:\s*\(\)\s*=>\s*setState\(\(\)\s*=>\s*selectedScene\s*=\s*index\),",
        "onTap: () => _selectScene(index),",
        "timeline selection",
    )

    # The export button must use edited scene text and style.
    main = sub_once(
        main,
        r"sceneTitles:\s*buildSceneTitles\(\s*widget\.projectInput\.isNotEmpty\s*\?\s*widget\.projectInput\s*:\s*widget\.projectTitle,\s*sceneCount,\s*\),",
        "sceneTitles: _currentSceneTitles(),\n              style: style,",
        "editor export scene list",
    )

    # Replace the scene/script placeholder panels with an editor.
    main = sub_once(
        main,
        r"      case 'Scenes':\s*return Text\(.*?;\s*case 'Script':\s*return const Text\(.*?;\s*case 'Subtitles':",
        """      case 'Scenes':
      case 'Script':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              activeTool == 'Scenes'
                  ? 'Edit scene ${selectedScene + 1}'
                  : 'Edit narration for this scene',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: sceneTextController,
              minLines: 4,
              maxLines: 10,
              maxLength: 3500,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(
                hintText: activeTool == 'Scenes'
                    ? 'Describe this scene...'
                    : 'Write the narration for this scene...',
                alignLabelWithHint: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onChanged: (_) => _saveSelectedSceneText(),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: selectedScene > 0
                        ? () => _moveSelectedScene(-1)
                        : null,
                    icon: const Icon(Icons.arrow_back),
                    label: const Text('Move earlier'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: selectedScene < sceneTitles.length - 1
                        ? () => _moveSelectedScene(1)
                        : null,
                    icon: const Icon(Icons.arrow_forward),
                    label: const Text('Move later'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Edited scene text is used for narration and displayed in the '
              'current illustrated renderer.',
              style: TextStyle(color: muted, fontSize: 12, height: 1.5),
            ),
          ],
        );
      case 'Subtitles':""",
        "scene and script panels",
        re.S,
    )

    # The renderer accepts the chosen visual style.
    exporter = sub_once(
        exporter,
        r"(static Future<File> exportTitleCardVideo\(\s*\{\s*required String title,)",
        r"\1\n    String style = 'Cinematic Realism',",
        "exporter signature",
        re.S,
    )

    exporter = sub_once(
        exporter,
        r"(await _drawSceneCard\(\s*file: imageFile,)",
        r"\1\n          style: style,",
        "scene card call",
    )

    exporter = sub_once(
        exporter,
        r"(static Future<void> _drawSceneCard\(\s*\{\s*required File file,)",
        r"\1\n    required String style,",
        "scene card signature",
        re.S,
    )

    palette_pattern = (
        r"    // Rotate through several premium historical palettes\.\s*"
        r"// These are stylized illustrations, not photographs or AI footage\.\s*"
        r"final palettes = <List<Color>>\[\s*"
        r"\[const Color\(0xFF34302A\), const Color\(0xFF171513\), const Color\(0xFF080909\)\],\s*"
        r"\[const Color\(0xFF27343B\), const Color\(0xFF131C22\), const Color\(0xFF080B0E\)\],\s*"
        r"\[const Color\(0xFF393026\), const Color\(0xFF1B1713\), const Color\(0xFF090909\)\],\s*"
        r"\[const Color\(0xFF302D37\), const Color\(0xFF19171F\), const Color\(0xFF080909\)\],\s*"
        r"\];\s*final palette = palettes\[\(sceneNumber - 1\) % palettes\.length\];"
    )

    palette_replacement = """    // Style-specific palettes. These remain illustrated scenes, not AI footage.
    final normalizedStyle = style.toLowerCase();
    final palette = normalizedStyle == 'dark history'
        ? <Color>[const Color(0xFF202020), const Color(0xFF101010), const Color(0xFF050505)]
        : normalizedStyle == 'african history'
            ? <Color>[const Color(0xFF59402C), const Color(0xFF2D2118), const Color(0xFF100D09)]
            : normalizedStyle == 'documentary'
                ? <Color>[const Color(0xFF34434A), const Color(0xFF1B272D), const Color(0xFF080D10)]
                : normalizedStyle == '3d animation'
                    ? <Color>[const Color(0xFF66502D), const Color(0xFF30261A), const Color(0xFF100D09)]
                    : normalizedStyle == 'ancient world'
                        ? <Color>[const Color(0xFF685034), const Color(0xFF302418), const Color(0xFF100C08)]
                        : normalizedStyle == 'epic history'
                            ? <Color>[const Color(0xFF55352D), const Color(0xFF2A1B18), const Color(0xFF0C0908)]
                            : normalizedStyle == 'historical illustration'
                                ? <Color>[const Color(0xFF48423A), const Color(0xFF27231E), const Color(0xFF0C0B09)]
                                : <Color>[const Color(0xFF34302A), const Color(0xFF171513), const Color(0xFF080909)];"""

    exporter = sub_once(
        exporter,
        palette_pattern,
        palette_replacement,
        "renderer palette",
        re.S,
    )

except Exception as exc:
    print(f"PATCH NOT APPLIED: {exc}")
    print("Source files have not been written.")
    sys.exit(1)

# Preserve originals before writing either source file.
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = ROOT / "backups" / f"editor_patch_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=False)
shutil.copy2(main_path, backup_dir / "main.dart")
shutil.copy2(export_path, backup_dir / "video_exporter.dart")

# Prepare temporary candidates before replacing originals.
main_tmp = main_path.with_name("main.dart.patch-tmp")
export_tmp = export_path.with_name("video_exporter.dart.patch-tmp")

main_tmp.write_text(main)
export_tmp.write_text(exporter)

main_tmp.replace(main_path)
export_tmp.replace(export_path)

print("PATCH APPLIED")
print(f"Original files backed up in: {backup_dir}")
print("Scene editing, selection, reordering, preview/export inputs, and style palettes updated.")
print("Subtitles, music controls, transitions, voice selection, and project persistence remain pending.")
