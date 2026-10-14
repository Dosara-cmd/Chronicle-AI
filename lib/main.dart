import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:video_player/video_player.dart';
import 'package:share_plus/share_plus.dart';
import 'services/video_exporter.dart';
import 'services/narration_service.dart';
import 'services/video_library_service.dart';
import 'services/project_storage_service.dart';

void main() {
  runApp(const ChronicleAI());
}

const Color bg = Color(0xFF101112);
const Color surface = Color(0xFF191A1C);
const Color surface2 = Color(0xFF222427);
const Color gold = Color(0xFFD8B46A);
const Color muted = Color(0xFF9A9CA2);

class ChronicleAI extends StatelessWidget {
  const ChronicleAI({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chronicle AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: bg,
        colorScheme: const ColorScheme.dark(
          primary: gold,
          secondary: gold,
          surface: surface,
        ),
        fontFamily: 'Roboto',
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: surface2,
          hintStyle: const TextStyle(color: muted),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Colors.white10),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: gold),
          ),
          contentPadding: const EdgeInsets.all(16),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

class AppMark extends StatelessWidget {
  const AppMark({super.key, this.size = 48});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: gold.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(size * 0.28),
        border: Border.all(color: gold.withValues(alpha: 0.45)),
      ),
      child: Icon(
        Icons.account_balance_rounded,
        color: gold,
        size: size * 0.57,
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int tab = 0;

  final List<Widget> screens = const [HomeDashboard(), ProjectsScreen()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: IndexedStack(index: tab, children: screens),
      ),
      bottomNavigationBar: NavigationBar(
        backgroundColor: surface,
        indicatorColor: gold.withValues(alpha: 0.15),
        selectedIndex: tab,
        onDestinationSelected: (value) {
          setState(() => tab = value);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.auto_awesome_outlined),
            selectedIcon: Icon(Icons.auto_awesome),
            label: 'Create',
          ),
          NavigationDestination(
            icon: Icon(Icons.video_library_outlined),
            selectedIcon: Icon(Icons.video_library),
            label: 'My Videos',
          ),
        ],
      ),
    );
  }
}

class HomeDashboard extends StatelessWidget {
  const HomeDashboard({super.key});

  void open(BuildContext context, Widget screen) {
    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => screen));
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(20, 22, 20, 28),
          sliver: SliverList(
            delegate: SliverChildListDelegate([
              Row(
                children: [
                  const AppMark(),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'CHRONICLE AI',
                          style: TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 1.4,
                          ),
                        ),
                        SizedBox(height: 3),
                        Text(
                          'BRING THE PAST TO LIFE',
                          style: TextStyle(
                            color: gold,
                            fontSize: 9,
                            letterSpacing: 1.8,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    tooltip: 'About Chronicle AI',
                    onPressed: () => showAboutDialog(
                      context: context,
                      applicationName: 'Chronicle AI',
                      applicationVersion: '0.1.0',
                      applicationLegalese: 'A history video creation studio.',
                    ),
                    icon: const Icon(Icons.info_outline),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [const Color(0xFF332B1D), surface, surface],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: gold.withValues(alpha: 0.25)),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.history_edu_rounded, color: gold, size: 34),
                    SizedBox(height: 20),
                    Text(
                      'History deserves\nto be seen.',
                      style: TextStyle(
                        fontSize: 30,
                        height: 1.15,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.8,
                      ),
                    ),
                    SizedBox(height: 12),
                    Text(
                      'Turn historical stories into vertical videos '
                      'for TikTok and other platforms.',
                      style: TextStyle(color: muted, fontSize: 14, height: 1.6),
                    ),
                    SizedBox(height: 18),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        MiniTag(icon: Icons.smartphone, text: '9:16 VIDEO'),
                        MiniTag(icon: Icons.schedule, text: '2–3 MIN'),
                        MiniTag(icon: Icons.auto_awesome, text: 'AI STUDIO'),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 30),
              const SectionHeading(
                title: 'Create a video',
                subtitle: 'Choose how you want to begin.',
              ),
              const SizedBox(height: 16),
              GeneratorCard(
                icon: Icons.bolt_rounded,
                label: '01 / AUTOMATIC',
                title: 'Automatic AI Generator',
                description:
                    'Enter a historical topic. Build your story '
                    'from a simple prompt.',
                onTap: () => open(context, const AutomaticGeneratorScreen()),
              ),
              const SizedBox(height: 14),
              GeneratorCard(
                icon: Icons.edit_note_rounded,
                label: '02 / YOUR SCRIPT',
                title: 'Paste AI Generator',
                description:
                    'Already have a script? Paste it and prepare '
                    'it for a historical video.',
                onTap: () => open(context, const PasteGeneratorScreen()),
              ),
              const SizedBox(height: 30),
              const SectionHeading(
                title: 'Your creative studio',
                subtitle: 'Everything you need, in one place.',
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: SmallFeatureCard(
                      icon: Icons.record_voice_over_rounded,
                      title: 'AI Voices',
                      subtitle: 'Choose narration',
                      onTap: () => open(context, const VoiceSelectionScreen()),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: SmallFeatureCard(
                      icon: Icons.movie_creation_outlined,
                      title: 'Video Styles',
                      subtitle: 'Find your look',
                      onTap: () => open(context, const StyleSelectionScreen()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SmallFeatureCard(
                icon: Icons.tune_rounded,
                title: 'Editing Studio',
                subtitle: 'Preview the editing workspace',
                wide: true,
                onTap: () => open(context, const EditorScreen()),
              ),
              const SizedBox(height: 24),
              const Center(
                child: Text(
                  'CHRONICLE AI  •  VERSION 0.1',
                  style: TextStyle(
                    color: muted,
                    fontSize: 10,
                    letterSpacing: 1.4,
                  ),
                ),
              ),
            ]),
          ),
        ),
      ],
    );
  }
}

class MiniTag extends StatelessWidget {
  const MiniTag({super.key, required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black26,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: gold),
          const SizedBox(width: 6),
          Text(
            text,
            style: const TextStyle(
              fontSize: 9,
              letterSpacing: 0.8,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class SectionHeading extends StatelessWidget {
  const SectionHeading({
    super.key,
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 5),
        Text(subtitle, style: const TextStyle(color: muted, fontSize: 13)),
      ],
    );
  }
}

class GeneratorCard extends StatelessWidget {
  const GeneratorCard({
    super.key,
    required this.icon,
    required this.label,
    required this.title,
    required this.description,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String title;
  final String description;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: surface,
      borderRadius: BorderRadius.circular(22),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(22),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: Colors.white10),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: gold.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Icon(icon, color: gold, size: 26),
                  ),
                  const Spacer(),
                  const Icon(
                    Icons.arrow_outward_rounded,
                    color: gold,
                    size: 21,
                  ),
                ],
              ),
              const SizedBox(height: 18),
              Text(
                label,
                style: const TextStyle(
                  color: gold,
                  fontSize: 10,
                  letterSpacing: 1.4,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 7),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: const TextStyle(color: muted, height: 1.5, fontSize: 13),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class SmallFeatureCard extends StatelessWidget {
  const SmallFeatureCard({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.wide = false,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool wide;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: surface,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: Colors.white10),
          ),
          child: Row(
            children: [
              Icon(icon, color: gold, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: const TextStyle(color: muted, fontSize: 11),
                    ),
                  ],
                ),
              ),
              if (wide) const Icon(Icons.chevron_right_rounded, color: muted),
            ],
          ),
        ),
      ),
    );
  }
}

class PageFrame extends StatelessWidget {
  const PageFrame({
    super.key,
    required this.title,
    required this.subtitle,
    required this.child,
  });

  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: bg,
        title: const Text(
          'CHRONICLE AI',
          style: TextStyle(
            fontSize: 13,
            letterSpacing: 1.6,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 27,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.6,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: const TextStyle(color: muted, height: 1.5, fontSize: 14),
            ),
            const SizedBox(height: 26),
            child,
          ],
        ),
      ),
    );
  }
}

class AutomaticGeneratorScreen extends StatefulWidget {
  const AutomaticGeneratorScreen({super.key});

  @override
  State<AutomaticGeneratorScreen> createState() =>
      _AutomaticGeneratorScreenState();
}

class _AutomaticGeneratorScreenState extends State<AutomaticGeneratorScreen> {
  final topicController = TextEditingController();
  final descriptionController = TextEditingController();
  String duration = '3 minutes';
  String style = 'Cinematic Realism';
  String voice = 'Deep Documentary';

  @override
  void dispose() {
    topicController.dispose();
    descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Automatic generator',
      subtitle: 'Start with a topic. Prepare your historical video settings.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const FieldLabel('WHAT IS YOUR VIDEO ABOUT?'),
          TextField(
            controller: topicController,
            maxLines: 3,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText: 'e.g. The rise and fall of the Mali Empire',
              prefixIcon: Icon(Icons.history_edu_rounded),
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 22),
          const FieldLabel('VIDEO DESCRIPTION'),
          TextField(
            controller: descriptionController,
            minLines: 2,
            maxLines: 4,
            maxLength: 300,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText:
                  'Write a short caption for TikTok or other platforms...',
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
          const FieldLabel('VIDEO DURATION'),
          ChoiceChips(
            options: const [
              '1 minute',
              '2 minutes',
              '3 minutes',
              '4 minutes',
              '5 minutes',
            ],
            selected: duration,
            onSelected: (value) => setState(() => duration = value),
          ),
          const SizedBox(height: 24),
          const FieldLabel('VISUAL STYLE'),
          SelectionTile(
            icon: Icons.movie_creation_outlined,
            title: style,
            subtitle: 'Choose the visual appearance',
            onTap: () async {
              final result = await Navigator.push<String>(
                context,
                MaterialPageRoute(
                  builder: (_) => StyleSelectionScreen(initialStyle: style),
                ),
              );
              if (result != null) setState(() => style = result);
            },
          ),
          const SizedBox(height: 18),
          const FieldLabel('NARRATOR'),
          SelectionTile(
            icon: Icons.record_voice_over_rounded,
            title: voice,
            subtitle: 'Choose the narration voice',
            onTap: () async {
              final result = await Navigator.push<String>(
                context,
                MaterialPageRoute(
                  builder: (_) => VoiceSelectionScreen(initialVoice: voice),
                ),
              );
              if (result != null) setState(() => voice = result);
            },
          ),
          const SizedBox(height: 26),
          const NoticeCard(
            text:
                'Your final video will target vertical 9:16 format. '
                'AI generation must be connected before a real video '
                'can be produced.',
          ),
          const SizedBox(height: 24),
          PrimaryButton(
            label: 'Prepare Video',
            icon: Icons.auto_awesome,
            onPressed: () {
              if (topicController.text.trim().isEmpty) {
                showMessage(context, 'Please enter a history topic.');
                return;
              }
              Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => PreparationScreen(
                    topic: topicController.text.trim(),
                    style: style,
                    voice: voice,
                    duration: duration,
                    description: descriptionController.text.trim().isEmpty
                        ? buildVideoDescription(topicController.text.trim())
                        : descriptionController.text.trim(),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class PasteGeneratorScreen extends StatefulWidget {
  const PasteGeneratorScreen({super.key});

  @override
  State<PasteGeneratorScreen> createState() => _PasteGeneratorScreenState();
}

class _PasteGeneratorScreenState extends State<PasteGeneratorScreen> {
  final scriptController = TextEditingController();
  final descriptionController = TextEditingController();
  String duration = '3 minutes';
  String style = 'Cinematic Realism';
  String voice = 'Deep Documentary';

  @override
  void dispose() {
    scriptController.dispose();
    descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Paste your script',
      subtitle: 'Bring your existing story and prepare it for a video.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const FieldLabel('YOUR HISTORY SCRIPT'),
          TextField(
            controller: scriptController,
            minLines: 9,
            maxLines: 16,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText: 'Paste your complete historical story here...',
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 10),
          AnimatedBuilder(
            animation: scriptController,
            builder: (context, _) {
              final count = scriptController.text
                  .trim()
                  .split(RegExp(r'\s+'))
                  .where((word) => word.isNotEmpty)
                  .length;
              return Text(
                '${scriptController.text.length} characters • '
                '${scriptController.text.trim().isEmpty ? 0 : count} words',
                style: const TextStyle(color: muted, fontSize: 12),
              );
            },
          ),
          const SizedBox(height: 22),
          const FieldLabel('VIDEO DESCRIPTION'),
          TextField(
            controller: descriptionController,
            minLines: 2,
            maxLines: 4,
            maxLength: 300,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
              hintText:
                  'Write a short caption for TikTok or other platforms...',
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
          const FieldLabel('VIDEO DURATION'),
          ChoiceChips(
            options: const [
              '1 minute',
              '2 minutes',
              '3 minutes',
              '4 minutes',
              '5 minutes',
            ],
            selected: duration,
            onSelected: (value) => setState(() => duration = value),
          ),
          const SizedBox(height: 24),
          const FieldLabel('VISUAL STYLE'),
          SelectionTile(
            icon: Icons.palette_outlined,
            title: style,
            subtitle: 'Choose a historical look',
            onTap: () async {
              final result = await Navigator.push<String>(
                context,
                MaterialPageRoute(
                  builder: (_) => StyleSelectionScreen(initialStyle: style),
                ),
              );
              if (result != null) setState(() => style = result);
            },
          ),
          const SizedBox(height: 18),
          const FieldLabel('NARRATOR'),
          SelectionTile(
            icon: Icons.graphic_eq_rounded,
            title: voice,
            subtitle: 'Choose your narration voice',
            onTap: () async {
              final result = await Navigator.push<String>(
                context,
                MaterialPageRoute(
                  builder: (_) => VoiceSelectionScreen(initialVoice: voice),
                ),
              );
              if (result != null) setState(() => voice = result);
            },
          ),
          const SizedBox(height: 26),
          PrimaryButton(
            label: 'Prepare My Script',
            icon: Icons.movie_filter_outlined,
            onPressed: () {
              final script = scriptController.text.trim();
              if (script.isEmpty) {
                showMessage(context, 'Please paste your script.');
                return;
              }
              Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => PreparationScreen(
                    topic: script,
                    style: style,
                    voice: voice,
                    duration: duration,
                    description: descriptionController.text.trim().isEmpty
                        ? buildVideoDescription(script)
                        : descriptionController.text.trim(),
                    pastedScript: true,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

List<String> buildSceneTitles(String input, int sceneCount) {
  final cleanInput = input.trim();
  final count = sceneCount.clamp(1, 20);

  if (cleanInput.isEmpty) {
    return List.generate(count, (index) => 'Historical chapter ${index + 1}');
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

String buildVideoDescription(String input) {
  final clean = input.trim().replaceAll(RegExp(r'\s+'), ' ');
  final firstSentence = clean.split(RegExp(r'(?<=[.!?])\s+')).first.trim();
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

Future<void> renderAndShareVideo(
  BuildContext context, {
  String style = 'Cinematic Realism',
  required String title,
  required List<String> sceneTitles,
  List<String>? sceneDescriptions,
  List<String>? subtitleTexts,
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
        content: Row(
          children: [
            SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(color: gold),
            ),
            SizedBox(width: 16),
            Expanded(child: Text('Creating narration and rendering video...')),
          ],
        ),
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
      style: style,
      sceneTitles: sceneTitles,
      sceneDescriptions: sceneDescriptions,
      subtitleTexts: subtitleTexts,
      secondsPerScene: perScene,
      totalDurationSeconds: seconds,
      narrationAudioPaths: narrationPaths,
    );

    if (context.mounted && dialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
      dialogOpen = false;
    }
    if (!context.mounted) return;

    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ChronicleVideoPreviewScreen(
          file: file,
          title: title,
          description: description,
        ),
      ),
    );
  } catch (error) {
    if (context.mounted && dialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
    }
    if (context.mounted) showMessage(context, 'Export failed: $error');
  } finally {
    await ChronicleNarrationService.deleteFiles(narrationPaths);
  }
}

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
  bool _savingVideo = false;

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

  Future<void> _saveVideoToPhone() async {
    if (_savingVideo) return;

    setState(() => _savingVideo = true);

    try {
      final safeTitle = widget.title
          .replaceAll(RegExp(r'[\\/:*?"<>|]'), '_')
          .trim();
      final timestamp = DateTime.now()
          .toIso8601String()
          .replaceAll(':', '-')
          .replaceAll('.', '-');

      final name =
          '${safeTitle.isEmpty ? "Chronicle" : safeTitle}'
          '_$timestamp.mp4';

      await VideoLibraryService.saveVideo(
        sourcePath: widget.file.path,
        displayName: name,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Video saved to Movies/Chronicle AI.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } on PlatformException catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            error.message ?? 'Unable to save the video to your phone.',
          ),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not save video: $error'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) setState(() => _savingVideo = false);
    }
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
            OutlinedButton.icon(
              onPressed: _savingVideo ? null : _saveVideoToPhone,
              icon: _savingVideo
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: gold,
                      ),
                    )
                  : const Icon(Icons.save_alt_rounded),
              label: Text(_savingVideo ? 'Saving video...' : 'Save to phone'),
              style: OutlinedButton.styleFrom(
                foregroundColor: gold,
                side: BorderSide(color: gold.withValues(alpha: 0.65)),
                minimumSize: const Size.fromHeight(52),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Temporary preview file: ${widget.file.path}',
              style: const TextStyle(color: muted, fontSize: 11),
            ),
          ],
        ),
      ),
    );
  }
}

class PreparationScreen extends StatelessWidget {
  const PreparationScreen({
    super.key,
    required this.topic,
    required this.style,
    required this.voice,
    required this.duration,
    this.pastedScript = false,
    this.description = '',
  });

  final String topic;
  final String style;
  final String voice;
  final String duration;
  final bool pastedScript;
  final String description;

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Video settings',
      subtitle: 'Review your selections before generation is connected.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const NoticeCard(
            text:
                'This preview confirms your project settings. '
                'It does not generate an AI video yet.',
          ),
          const SizedBox(height: 22),
          const FieldLabel('PROJECT INPUT'),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              pastedScript ? 'Pasted script' : topic,
              maxLines: 8,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(height: 1.5),
            ),
          ),
          const SizedBox(height: 18),
          DetailRow(label: 'Duration', value: duration),
          DetailRow(label: 'Style', value: style),
          DetailRow(label: 'Voice', value: voice),
          const DetailRow(label: 'Aspect ratio', value: '9:16 vertical'),
          const SizedBox(height: 24),
          PrimaryButton(
            label: 'Open Editing Studio',
            icon: Icons.tune_rounded,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute<void>(
                builder: (_) => EditorScreen(
                  projectTitle: pastedScript ? 'Pasted script' : topic,
                  projectInput: topic,
                  selectedStyle: style,
                  selectedVoice: voice,
                  duration: duration,
                  description: description,
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => renderAndShareVideo(
              context,
              title: topic.trim().isEmpty ? 'Chronicle History' : topic.trim(),
              style: style,
              voice: voice,
              sceneTitles: buildSceneTitles(topic, 4),
              duration: duration,
              description: description,
            ),
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Generate video'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(52),
              foregroundColor: gold,
              side: const BorderSide(color: gold),
            ),
          ),
        ],
      ),
    );
  }
}

const List<String> videoStyles = [
  'Cinematic Realism',
  'Epic History',
  'Dark History',
  'Documentary',
  'Ancient World',
  'African History',
  '3D Animation',
  'Historical Illustration',
];

class StyleSelectionScreen extends StatelessWidget {
  const StyleSelectionScreen({super.key, this.initialStyle});

  final String? initialStyle;

  static const icons = [
    Icons.movie_creation_outlined,
    Icons.castle_outlined,
    Icons.nightlight_round,
    Icons.menu_book_rounded,
    Icons.account_balance_rounded,
    Icons.public_rounded,
    Icons.animation_rounded,
    Icons.brush_rounded,
  ];

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Video styles',
      subtitle: 'Choose the visual direction for your story.',
      child: Column(
        children: List.generate(videoStyles.length, (index) {
          final style = videoStyles[index];
          final selected = style == initialStyle;

          return Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Material(
              color: surface,
              borderRadius: BorderRadius.circular(16),
              child: ListTile(
                leading: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: gold.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: Icon(icons[index], color: gold),
                ),
                title: Text(
                  style,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                subtitle: Text(
                  styleDescription(style),
                  style: const TextStyle(color: muted, fontSize: 11),
                ),
                trailing: Icon(
                  selected ? Icons.check_circle : Icons.chevron_right,
                  color: selected ? gold : muted,
                ),
                onTap: () => Navigator.pop(context, style),
              ),
            ),
          );
        }),
      ),
    );
  }
}

String styleDescription(String style) {
  switch (style) {
    case 'Cinematic Realism':
      return 'Film-inspired historical reconstructions';
    case 'Epic History':
      return 'Dramatic kingdoms, battles and empires';
    case 'Dark History':
      return 'Moody historical mysteries';
    case 'Documentary':
      return 'Clear educational presentation';
    case 'Ancient World':
      return 'Civilizations of the ancient world';
    case 'African History':
      return 'Stories of African kingdoms and cultures';
    case '3D Animation':
      return 'Animated characters and environments';
    default:
      return 'Painting-inspired historical visuals';
  }
}

const List<String> voices = [
  'Deep Documentary',
  'Warm Storyteller',
  'Dramatic Narrator',
  'Calm Narrator',
  'Energetic Narrator',
  'Female Documentary',
  'British English',
  'American English',
];

class VoiceSelectionScreen extends StatelessWidget {
  const VoiceSelectionScreen({super.key, this.initialVoice});

  final String? initialVoice;

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Choose a voice',
      subtitle:
          'Choose a narration style. Actual voice playback will be '
          'available when a compatible free voice engine is connected.',
      child: Column(
        children: List.generate(voices.length, (index) {
          final voice = voices[index];
          final selected = voice == initialVoice;

          return Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Material(
              color: surface,
              borderRadius: BorderRadius.circular(16),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: gold.withValues(alpha: 0.12),
                  child: Icon(
                    index % 2 == 0 ? Icons.record_voice_over : Icons.graphic_eq,
                    color: gold,
                  ),
                ),
                title: Text(
                  voice,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                subtitle: Text(
                  voiceDescription(voice),
                  style: const TextStyle(color: muted, fontSize: 11),
                ),
                trailing: Icon(
                  selected ? Icons.check_circle : Icons.chevron_right,
                  color: selected ? gold : muted,
                ),
                onTap: () => Navigator.pop(context, voice),
              ),
            ),
          );
        }),
      ),
    );
  }
}

String voiceDescription(String voice) {
  switch (voice) {
    case 'Deep Documentary':
      return 'Deep, authoritative delivery';
    case 'Warm Storyteller':
      return 'Friendly, engaging narration';
    case 'Dramatic Narrator':
      return 'Expressive cinematic storytelling';
    case 'Calm Narrator':
      return 'Measured, educational delivery';
    case 'Energetic Narrator':
      return 'Lively short-form storytelling';
    case 'Female Documentary':
      return 'Clear, professional female narration';
    case 'British English':
      return 'British English voice preference';
    default:
      return 'American English voice preference';
  }
}

class EditorScreen extends StatefulWidget {
  const EditorScreen({
    super.key,
    this.projectTitle = 'Untitled history video',
    this.projectInput = '',
    this.selectedStyle = 'Cinematic Realism',
    this.selectedVoice = 'Deep Documentary',
    this.duration = '3 minutes',
    this.description = '',
    this.projectId = '',
    this.initialSceneTexts,
    this.initialSceneDescriptions,
    this.initialSubtitleTexts,
  });

  final String projectId;
  final List<String>? initialSceneTexts;
  final List<String>? initialSceneDescriptions;
  final List<String>? initialSubtitleTexts;
  final String projectTitle;
  final String projectInput;
  final String selectedStyle;
  final String selectedVoice;

  final String duration;
  final String description;
  @override
  State<EditorScreen> createState() => _EditorScreenState();
}

class _EditorScreenState extends State<EditorScreen> {
  int selectedScene = 0;
  String style = '';
  late List<String> sceneTitles;
  late List<String> sceneDescriptions;
  late List<String> subtitleTexts;
  late String currentProjectId;
  late final TextEditingController sceneTextController;
  late final TextEditingController sceneDescriptionController;
  late final TextEditingController subtitleTextController;
  String voice = '';
  String activeTool = 'Scenes';
  late final TextEditingController descriptionController;

  @override
  void initState() {
    super.initState();
    style = widget.selectedStyle;
    voice = widget.selectedVoice;
    currentProjectId = widget.projectId;
    sceneTitles = widget.initialSceneTexts != null &&
            widget.initialSceneTexts!.isNotEmpty
        ? List<String>.from(widget.initialSceneTexts!)
        : buildSceneTitles(
            widget.projectInput.trim().isNotEmpty
                ? widget.projectInput
                : widget.projectTitle,
            4,
          );
    sceneDescriptions = _initialTrack(
      widget.initialSceneDescriptions,
      sceneTitles,
    );
    subtitleTexts = _initialTrack(
      widget.initialSubtitleTexts,
      sceneTitles,
    );
    sceneTextController = TextEditingController(text: sceneTitles.first);
    sceneDescriptionController = TextEditingController(
      text: sceneDescriptions.first,
    );
    subtitleTextController = TextEditingController(
      text: subtitleTexts.first,
    );
    descriptionController = TextEditingController(
      text: widget.description.trim().isNotEmpty
          ? widget.description
          : buildVideoDescription(
              widget.projectInput.isNotEmpty
                  ? widget.projectInput
                  : widget.projectTitle,
            ),
    );
  }

  List<String> _initialTrack(
    List<String>? saved,
    List<String> fallback,
  ) {
    if (saved != null && saved.length == fallback.length) {
      return List<String>.from(saved);
    }
    return List<String>.from(fallback);
  }

  @override
  void dispose() {
    descriptionController.dispose();
    sceneTextController.dispose();
    sceneDescriptionController.dispose();
    subtitleTextController.dispose();
    super.dispose();
  }

  Future<void> _saveProject() async {
    try {
      final scenes = _currentSceneTitles();
      if (scenes.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Add at least one non-empty scene first.')),
        );
        return;
      }

      if (currentProjectId.isEmpty) {
        currentProjectId = DateTime.now().microsecondsSinceEpoch.toString();
      }

      await ChronicleProjectStorage.save(
        ChronicleProject(
          id: currentProjectId,
          title: widget.projectTitle.trim().isEmpty
              ? 'Untitled history video'
              : widget.projectTitle.trim(),
          input: widget.projectInput,
          style: style,
          voice: voice,
          duration: widget.duration,
          description: descriptionController.text.trim(),
          sceneTexts: List<String>.from(sceneTitles),
          sceneDescriptions: _currentSceneDescriptions(),
          subtitleTexts: _currentSubtitleTexts(),
          updatedAt: DateTime.now(),
        ),
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Project saved on this device.')),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not save project: $error')),
      );
    }
  }

  void _saveSelectedSceneText() {
    if (sceneTitles.isEmpty ||
        selectedScene < 0 ||
        selectedScene >= sceneTitles.length) {
      return;
    }
    sceneTitles[selectedScene] = sceneTextController.text.trim();
    sceneDescriptions[selectedScene] =
        sceneDescriptionController.text.trim();
    subtitleTexts[selectedScene] = subtitleTextController.text.trim();
  }

  void _selectScene(int index) {
    if (index < 0 || index >= sceneTitles.length) return;
    _saveSelectedSceneText();
    setState(() {
      selectedScene = index;
      sceneTextController.text = sceneTitles[index];
      sceneDescriptionController.text = sceneDescriptions[index];
      subtitleTextController.text = subtitleTexts[index];
      sceneTextController.selection = TextSelection.collapsed(
        offset: sceneTextController.text.length,
      );
    });
  }

  void _addScene() {
    _saveSelectedSceneText();
    if (sceneTitles.length >= 20) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('A project can contain up to 20 scenes.')),
      );
      return;
    }
    setState(() {
      const newScene = 'New historical scene';
      sceneTitles.add(newScene);
      sceneDescriptions.add(newScene);
      subtitleTexts.add(newScene);
      selectedScene = sceneTitles.length - 1;
      sceneTextController.text = newScene;
      sceneDescriptionController.text = newScene;
      subtitleTextController.text = newScene;
    });
  }

  void _moveSelectedScene(int direction) {
    _saveSelectedSceneText();
    final destination = selectedScene + direction;
    if (destination < 0 || destination >= sceneTitles.length) return;
    setState(() {
      final title = sceneTitles.removeAt(selectedScene);
      sceneTitles.insert(destination, title);

      final sceneDescription = sceneDescriptions.removeAt(selectedScene);
      sceneDescriptions.insert(destination, sceneDescription);

      final subtitle = subtitleTexts.removeAt(selectedScene);
      subtitleTexts.insert(destination, subtitle);

      selectedScene = destination;
      sceneTextController.text = sceneTitles[selectedScene];
      sceneDescriptionController.text = sceneDescriptions[selectedScene];
      subtitleTextController.text = subtitleTexts[selectedScene];
    });
  }

  List<String> _currentSceneDescriptions() {
    _saveSelectedSceneText();
    return List<String>.from(sceneDescriptions);
  }

  List<String> _currentSubtitleTexts() {
    _saveSelectedSceneText();
    return List<String>.from(subtitleTexts);
  }

  List<String> _currentSceneTitles() {
    _saveSelectedSceneText();
    return sceneTitles
        .map((scene) => scene.trim())
        .where((scene) => scene.isNotEmpty)
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Editing studio',
      subtitle: widget.projectTitle,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ChronicleEditorPreview(
            onGenerate: () => renderAndShareVideo(
              context,
              title: widget.projectTitle,
              sceneTitles: _currentSceneTitles(),
              sceneDescriptions: _currentSceneDescriptions(),
              subtitleTexts: _currentSubtitleTexts(),
              style: style,
              duration: widget.duration,
              description: descriptionController.text,
              voice: voice,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              const Icon(Icons.movie_outlined, color: gold),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'Scenes',
                  style: TextStyle(fontWeight: FontWeight.w800),
                ),
              ),
              IconButton(
                tooltip: 'Add scene',
                onPressed: _addScene,
                icon: const Icon(Icons.add_circle_outline, color: gold),
              ),
            ],
          ),
          const SizedBox(height: 10),
          SizedBox(
            height: 85,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: sceneTitles.length,
              separatorBuilder: (_, _) => const SizedBox(width: 10),
              itemBuilder: (context, index) {
                final selected = index == selectedScene;
                return InkWell(
                  onTap: () => _selectScene(index),
                  borderRadius: BorderRadius.circular(14),
                  child: Container(
                    width: 90,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: selected ? gold.withValues(alpha: 0.15) : surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: selected ? gold : Colors.white12,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.landscape_outlined,
                          color: selected ? gold : muted,
                        ),
                        const SizedBox(height: 5),
                        Text(
                          'Scene ${index + 1}',
                          style: const TextStyle(fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 24),
          const FieldLabel('EDITING TOOLS'),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children:
                [
                  'Scenes',
                  'Script',
                  'Voice',
                  'Subtitles',
                  'Music',
                  'Transitions',
                  'Style',
                  'Description',
                ].map((tool) {
                  return ChoiceChip(
                    label: Text(tool),
                    selected: activeTool == tool,
                    onSelected: (_) => setState(() => activeTool = tool),
                    selectedColor: gold.withValues(alpha: 0.2),
                    labelStyle: TextStyle(
                      color: activeTool == tool ? gold : Colors.white,
                    ),
                  );
                }).toList(),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: toolPanel(),
          ),
          const SizedBox(height: 22),
          OutlinedButton.icon(
            onPressed: _saveProject,
            icon: const Icon(Icons.save_outlined),
            label: const Text('Save project'),
            style: OutlinedButton.styleFrom(
              foregroundColor: gold,
              side: const BorderSide(color: gold),
              minimumSize: const Size.fromHeight(50),
            ),
          ),
          const SizedBox(height: 12),
          PrimaryButton(
            label: 'Export MP4',
            icon: Icons.download_rounded,
            onPressed: () => renderAndShareVideo(
              context,
              title: widget.projectTitle,
              voice: voice,
              sceneTitles: _currentSceneTitles(),
              sceneDescriptions: _currentSceneDescriptions(),
              subtitleTexts: _currentSubtitleTexts(),
              style: style,
              duration: widget.duration,
              description: descriptionController.text.trim(),
            ),
          ),
        ],
      ),
    );
  }

  Widget toolPanel() {
    switch (activeTool) {
      case 'Voice':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Narration voice'),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: voices.contains(voice) ? voice : voices.first,
              decoration: const InputDecoration(),
              items: voices
                  .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                  .toList(),
              onChanged: (value) {
                if (value != null) setState(() => voice = value);
              },
            ),
          ],
        );
      case 'Style':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Visual style'),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: videoStyles.contains(style)
                  ? style
                  : videoStyles.first,
              decoration: const InputDecoration(),
              items: videoStyles
                  .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                  .toList(),
              onChanged: (value) {
                if (value != null) setState(() => style = value);
              },
            ),
          ],
        );
      case 'Description':
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
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton.icon(
                  onPressed: () async {
                    final caption = descriptionController.text.trim();
                    if (caption.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Add a caption before copying it.'),
                        ),
                      );
                      return;
                    }
                    await Clipboard.setData(ClipboardData(text: caption));
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Caption copied to clipboard.'),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  },
                  icon: const Icon(Icons.copy_rounded),
                  label: const Text('Copy caption'),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'This caption is included when you share the exported video.',
                style: TextStyle(color: muted, fontSize: 12, height: 1.5),
              ),
          ],
        );
      case 'Scenes':
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
              controller: activeTool == 'Scenes'
                  ? sceneDescriptionController
                  : sceneTextController,
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
              onChanged: (value) {
                if (sceneTitles.isEmpty ||
                    selectedScene >= sceneTitles.length) {
                  return;
                }
                if (activeTool == 'Scenes') {
                  sceneDescriptions[selectedScene] = value.trim();
                } else {
                  sceneTitles[selectedScene] = value.trim();
                }
              },
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
      case 'Subtitles':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Subtitle for scene ${selectedScene + 1}',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: subtitleTextController,
              minLines: 2,
              maxLines: 5,
              maxLength: 500,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                hintText: 'Enter the subtitle for this scene...',
                alignLabelWithHint: true,
              ),
              onChanged: (value) {
                if (subtitleTexts.isNotEmpty &&
                    selectedScene < subtitleTexts.length) {
                  subtitleTexts[selectedScene] = value.trim();
                }
              },
            ),
            const SizedBox(height: 6),
            Text(
              'Subtitle text is passed to the current illustrated video renderer.',
              style: TextStyle(color: muted, fontSize: 12, height: 1.5),
            ),
          ],
        );
      case 'Music':
        return const Text(
          'Background music selection and audio mixing will be '
          'implemented with video rendering.',
          style: TextStyle(color: muted, height: 1.6),
        );
      default:
        return const Text(
          'Scene transitions will be connected to video rendering.',
          style: TextStyle(color: muted, height: 1.6),
        );
    }
  }
}

class ProjectsScreen extends StatefulWidget {
  const ProjectsScreen({super.key});

  @override
  State<ProjectsScreen> createState() => _ProjectsScreenState();
}

class _ProjectsScreenState extends State<ProjectsScreen> {
  late Future<List<ChronicleProject>> _projectsFuture;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    _projectsFuture = ChronicleProjectStorage.loadAll();
  }

  Future<void> _deleteProject(ChronicleProject project) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: surface2,
        title: const Text('Delete project?'),
        content: Text('Delete "${project.title}" from this device?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    await ChronicleProjectStorage.delete(project.id);
    if (!mounted) return;
    setState(_reload);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Project deleted.')),
    );
  }

  void _openProject(ChronicleProject project) {
    Navigator.push(
      context,
      MaterialPageRoute<void>(
        builder: (_) => EditorScreen(
          projectId: project.id,
          projectTitle: project.title,
          projectInput: project.input,
          selectedStyle: project.style,
          selectedVoice: project.voice,
          duration: project.duration,
          description: project.description,
          initialSceneTexts: project.sceneTexts,
          initialSceneDescriptions: project.sceneDescriptions,
          initialSubtitleTexts: project.subtitleTexts,
        ),
      ),
    ).then((_) {
      if (mounted) setState(_reload);
    });
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'My videos',
      subtitle: 'Saved history projects on this device.',
      child: FutureBuilder<List<ChronicleProject>>(
        future: _projectsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(color: gold),
              ),
            );
          }

          if (snapshot.hasError) {
            return NoticeCard(
              text: 'Could not load saved projects: ${snapshot.error}',
            );
          }

          final projects = snapshot.data ?? <ChronicleProject>[];
          if (projects.isEmpty) {
            return Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 42),
              decoration: BoxDecoration(
                color: surface,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: Colors.white10),
              ),
              child: const Column(
                children: [
                  Icon(Icons.video_library_outlined, color: gold, size: 52),
                  SizedBox(height: 18),
                  Text(
                    'Your story starts here',
                    style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Open a project in the Editing Studio and tap Save project. '
                    'Saved projects will appear here.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: muted, height: 1.6, fontSize: 13),
                  ),
                ],
              ),
            );
          }

          return Column(
            children: projects.map((project) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Container(
                  decoration: BoxDecoration(
                    color: surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white10),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 8,
                    ),
                    leading: const CircleAvatar(
                      backgroundColor: Color(0x22222222),
                      child: Icon(Icons.movie_creation_outlined, color: gold),
                    ),
                    title: Text(
                      project.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: Text(
                      '${project.style} • ${project.sceneTexts.length} scenes\n'
                      'Updated ${project.updatedAt.toLocal()}',
                      style: const TextStyle(color: muted, fontSize: 11),
                    ),
                    isThreeLine: true,
                    onTap: () => _openProject(project),
                    trailing: PopupMenuButton<String>(
                      onSelected: (value) {
                        if (value == 'open') _openProject(project);
                        if (value == 'delete') _deleteProject(project);
                      },
                      itemBuilder: (_) => const [
                        PopupMenuItem(value: 'open', child: Text('Open project')),
                        PopupMenuItem(value: 'delete', child: Text('Delete project')),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          );
        },
      ),
    );
  }
}

class FieldLabel extends StatelessWidget {
  const FieldLabel(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Text(
        text,
        style: const TextStyle(
          color: muted,
          fontSize: 10,
          letterSpacing: 1.4,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class ChoiceChips extends StatelessWidget {
  const ChoiceChips({
    super.key,
    required this.options,
    required this.selected,
    required this.onSelected,
  });

  final List<String> options;
  final String selected;
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: options.map((option) {
        final active = option == selected;
        return ChoiceChip(
          label: Text(option),
          selected: active,
          onSelected: (_) => onSelected(option),
          selectedColor: gold.withValues(alpha: 0.2),
          side: BorderSide(color: active ? gold : Colors.white12),
          labelStyle: TextStyle(
            color: active ? gold : Colors.white,
            fontWeight: FontWeight.w600,
          ),
        );
      }).toList(),
    );
  }
}

class SelectionTile extends StatelessWidget {
  const SelectionTile({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: surface,
      borderRadius: BorderRadius.circular(16),
      child: ListTile(
        onTap: onTap,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Colors.white10),
        ),
        leading: Icon(icon, color: gold),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Text(
          subtitle,
          style: const TextStyle(color: muted, fontSize: 11),
        ),
        trailing: const Icon(Icons.chevron_right, color: muted),
      ),
    );
  }
}

class NoticeCard extends StatelessWidget {
  const NoticeCard({super.key, required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: gold.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: gold.withValues(alpha: 0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline, color: gold, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: Colors.white70,
                height: 1.5,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class DetailRow extends StatelessWidget {
  const DetailRow({super.key, required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(
        children: [
          Expanded(
            child: Text(label, style: const TextStyle(color: muted)),
          ),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

class PrimaryButton extends StatelessWidget {
  const PrimaryButton({
    super.key,
    required this.label,
    required this.icon,
    required this.onPressed,
  });

  final String label;
  final IconData icon;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 54,
      child: FilledButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label, style: const TextStyle(fontWeight: FontWeight.w800)),
        style: FilledButton.styleFrom(
          backgroundColor: gold,
          foregroundColor: const Color(0xFF17130B),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

void showMessage(BuildContext context, String message) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        backgroundColor: surface2,
      ),
    );
}
