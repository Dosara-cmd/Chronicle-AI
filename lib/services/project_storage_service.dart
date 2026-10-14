import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

class ChronicleProject {
  const ChronicleProject({
    required this.id,
    required this.title,
    required this.input,
    required this.style,
    required this.voice,
    required this.duration,
    required this.description,
    required this.sceneTexts,
    this.sceneDescriptions = const <String>[],
    this.subtitleTexts = const <String>[],
    required this.updatedAt,
  });

  final String id;
  final String title;
  final String input;
  final String style;
  final String voice;
  final String duration;
  final String description;
  final List<String> sceneTexts;
  final List<String> sceneDescriptions;
  final List<String> subtitleTexts;
  final DateTime updatedAt;

  factory ChronicleProject.fromJson(Map<String, dynamic> json) {
    final rawScenes = json['sceneTexts'];
    final rawDescriptions = json['sceneDescriptions'];
    final rawSubtitles = json['subtitleTexts'];
    return ChronicleProject(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Untitled history video',
      input: json['input']?.toString() ?? '',
      style: json['style']?.toString() ?? 'Cinematic Realism',
      voice: json['voice']?.toString() ?? 'Deep Documentary',
      duration: json['duration']?.toString() ?? '3 minutes',
      description: json['description']?.toString() ?? '',
      sceneTexts: rawScenes is List
          ? rawScenes.map((value) => value.toString()).toList()
          : <String>[],
      sceneDescriptions: rawDescriptions is List
          ? rawDescriptions.map((value) => value.toString()).toList()
          : <String>[],
      subtitleTexts: rawSubtitles is List
          ? rawSubtitles.map((value) => value.toString()).toList()
          : <String>[],
      updatedAt: DateTime.tryParse(json['updatedAt']?.toString() ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'input': input,
        'style': style,
        'voice': voice,
        'duration': duration,
        'description': description,
        'sceneTexts': sceneTexts,
        'sceneDescriptions': sceneDescriptions,
        'subtitleTexts': subtitleTexts,
        'updatedAt': updatedAt.toIso8601String(),
      };
}

class ChronicleProjectStorage {
  ChronicleProjectStorage._();

  static Future<File> _storageFile() async {
    final documents = await getApplicationDocumentsDirectory();
    final folder = Directory('${documents.path}/chronicle_projects');
    if (!await folder.exists()) {
      await folder.create(recursive: true);
    }
    return File('${folder.path}/projects.json');
  }

  static Future<List<ChronicleProject>> loadAll() async {
    final file = await _storageFile();
    if (!await file.exists()) return <ChronicleProject>[];

    try {
      final decoded = jsonDecode(await file.readAsString());
      if (decoded is! List) return <ChronicleProject>[];

      final projects = <ChronicleProject>[];
      for (final item in decoded) {
        if (item is Map) {
          final project = ChronicleProject.fromJson(
            Map<String, dynamic>.from(item),
          );
          if (project.id.isNotEmpty) projects.add(project);
        }
      }
      projects.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
      return projects;
    } on FormatException {
      return <ChronicleProject>[];
    } on TypeError {
      return <ChronicleProject>[];
    }
  }

  static Future<void> save(ChronicleProject project) async {
    final projects = await loadAll();
    final index = projects.indexWhere((item) => item.id == project.id);
    if (index >= 0) {
      projects[index] = project;
    } else {
      projects.add(project);
    }

    projects.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    final file = await _storageFile();
    await file.writeAsString(
      jsonEncode(projects.map((item) => item.toJson()).toList()),
      flush: true,
    );
  }

  static Future<void> delete(String id) async {
    final projects = await loadAll();
    projects.removeWhere((item) => item.id == id);
    final file = await _storageFile();
    await file.writeAsString(
      jsonEncode(projects.map((item) => item.toJson()).toList()),
      flush: true,
    );
  }
}
