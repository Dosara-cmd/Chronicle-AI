from pathlib import Path
from datetime import datetime

renderer = Path("lib/services/video_exporter.dart")
source = renderer.read_text()

start_marker = "  static Future<void> _drawSceneCard({"

if start_marker not in source:
    raise SystemExit("STOP: Scene drawing function not found. No changes written.")

# This function is currently the final member of ChronicleVideoExporter.
# Verify the expected file ending before replacing anything.
ending = "\n  }\n}"
if not source.rstrip().endswith(ending):
    raise SystemExit(
        "STOP: Renderer ending differs from the expected structure. "
        "No changes written."
    )

start = source.index(start_marker)
new_function = r'''
  static Future<void> _drawSceneCard({
    required File file,
    required String projectTitle,
    required String sceneTitle,
    required int sceneNumber,
    required int totalScenes,
  }) async {
    final recorder = ui.PictureRecorder();
    final canvas = Canvas(
      recorder,
      Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
    );

    final bounds = Rect.fromLTWH(
      0,
      0,
      width.toDouble(),
      height.toDouble(),
    );

    // Rotate through several premium historical palettes.
    // These are stylized illustrations, not photographs or AI footage.
    final palettes = <List<Color>>[
      [const Color(0xFF34302A), const Color(0xFF171513), const Color(0xFF080909)],
      [const Color(0xFF27343B), const Color(0xFF131C22), const Color(0xFF080B0E)],
      [const Color(0xFF393026), const Color(0xFF1B1713), const Color(0xFF090909)],
      [const Color(0xFF302D37), const Color(0xFF19171F), const Color(0xFF080909)],
    ];
    final palette = palettes[(sceneNumber - 1) % palettes.length];
    final gold = const Color(0xFFD8B46A);
    final pale = const Color(0xFFE6DFD0);
    final muted = const Color(0xFFB6B6B6);

    canvas.drawRect(
      bounds,
      Paint()
        ..shader = ui.Gradient.linear(
          const Offset(0, 0),
          const Offset(720, 1280),
          palette,
          const [0.0, 0.52, 1.0],
        ),
    );

    // Atmospheric light behind the illustration.
    final sceneGlow = Paint()
      ..shader = ui.Gradient.radial(
        Offset(360 + ((sceneNumber % 3) - 1) * 70, 455),
        390,
        [
          gold.withOpacity(0.19),
          gold.withOpacity(0.045),
          const Color(0x00000000),
        ],
        const [0.0, 0.48, 1.0],
      );
    canvas.drawRect(bounds, sceneGlow);

    // Subtle vertical light rays.
    for (var i = 0; i < 7; i++) {
      final x = 100.0 + i * 87.0;
      final ray = Path()
        ..moveTo(x, 100)
        ..lineTo(x + 30, 100)
        ..lineTo(x + 150, 810)
        ..lineTo(x + 80, 810)
        ..close();
      canvas.drawPath(
        ray,
        Paint()..color = Colors.white.withOpacity(i.isEven ? 0.018 : 0.009),
      );
    }

    // A scene illustration changes according to historical subject keywords.
    final subject = '$projectTitle $sceneTitle'.toLowerCase();
    final isEgypt = subject.contains('egypt') ||
        subject.contains('pharaoh') ||
        subject.contains('pyramid');
    final isAfrica = subject.contains('africa') ||
        subject.contains('african') ||
        subject.contains('mali') ||
        subject.contains('songhai') ||
        subject.contains('ashanti') ||
        subject.contains('yoruba') ||
        subject.contains('benin empire') ||
        subject.contains('great zimbabwe') ||
        subject.contains('kush') ||
        subject.contains('aksum') ||
        subject.contains('zulu') ||
        subject.contains('kongo');
    final isWar = subject.contains('war') ||
        subject.contains('battle') ||
        subject.contains('army') ||
        subject.contains('soldier') ||
        subject.contains('revolution') ||
        subject.contains('invasion');
    final isSea = subject.contains('ocean') ||
        subject.contains('sea') ||
        subject.contains('ship') ||
        subject.contains('voyage') ||
        subject.contains('trade route') ||
        subject.contains('exploration');
    final isAncient = subject.contains('ancient') ||
        subject.contains('empire') ||
        subject.contains('kingdom') ||
        subject.contains('roman') ||
        subject.contains('greek') ||
        subject.contains('medieval');

    final silhouettePaint = Paint()
      ..color = const Color(0xFF090B0C).withOpacity(0.73);
    final detailPaint = Paint()
      ..color = gold.withOpacity(0.52)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    // Low horizon and atmospheric ground.
    final horizon = Path()
      ..moveTo(0, 650)
      ..quadraticBezierTo(160, 590, 310, 660)
      ..quadraticBezierTo(500, 720, 720, 620)
      ..lineTo(720, 880)
      ..lineTo(0, 880)
      ..close();
    canvas.drawPath(horizon, silhouettePaint);

    if (isEgypt) {
      // Pyramid silhouettes.
      for (var i = 0; i < 3; i++) {
        final x = 115.0 + i * 185;
        final base = 710.0 + (i == 1 ? 25 : 0);
        final top = Offset(x + 65, base - 190 - (i == 1 ? 45 : 0));
        final pyramid = Path()
          ..moveTo(top.dx, top.dy)
          ..lineTo(x, base)
          ..lineTo(x + 130, base)
          ..close();
        canvas.drawPath(
          pyramid,
          Paint()..color = const Color(0xFF080909).withOpacity(0.84),
        );
        canvas.drawLine(
          top,
          Offset(x + 65, base),
          detailPaint..color = gold.withOpacity(0.36),
        );
      }
      canvas.drawCircle(
        const Offset(550, 365),
        54,
        Paint()..color = gold.withOpacity(0.12),
      );
    } else if (isSea) {
      // Moonlit sea and ship silhouette.
      canvas.drawCircle(
        const Offset(510, 355),
        63,
        Paint()..color = pale.withOpacity(0.13),
      );
      for (var i = 0; i < 7; i++) {
        final y = 585.0 + i * 24;
        canvas.drawLine(
          Offset(80 + i * 12.0, y),
          Offset(630 - i * 9.0, y),
          Paint()
            ..color = gold.withOpacity(0.10 + i * 0.012)
            ..strokeWidth = 2,
        );
      }
      final ship = Path()
        ..moveTo(170, 565)
        ..lineTo(555, 565)
        ..lineTo(500, 625)
        ..lineTo(235, 625)
        ..close();
      canvas.drawPath(ship, silhouettePaint);
      canvas.drawLine(
        const Offset(365, 385),
        const Offset(365, 563),
        detailPaint,
      );
      final sail = Path()
        ..moveTo(355, 405)
        ..lineTo(245, 535)
        ..lineTo(355, 535)
        ..close();
      canvas.drawPath(
        sail,
        Paint()..color = gold.withOpacity(0.19),
      );
      final secondSail = Path()
        ..moveTo(375, 435)
        ..lineTo(470, 535)
        ..lineTo(375, 535)
        ..close();
      canvas.drawPath(
        secondSail,
        Paint()..color = pale.withOpacity(0.12),
      );
    } else if (isWar) {
      // Distant battlefield banners and shield-like forms.
      for (var i = 0; i < 5; i++) {
        final x = 125.0 + i * 112;
        canvas.drawLine(
          Offset(x, 455 + (i % 2) * 35),
          Offset(x, 700),
          Paint()
            ..color = gold.withOpacity(0.48)
            ..strokeWidth = 3,
        );
        final banner = Path()
          ..moveTo(x, 455 + (i % 2) * 35)
          ..lineTo(x + 50, 470 + (i % 2) * 35)
          ..lineTo(x, 500 + (i % 2) * 35)
          ..close();
        canvas.drawPath(
          banner,
          Paint()..color = gold.withOpacity(0.23),
        );
      }
      for (var i = 0; i < 4; i++) {
        final x = 145.0 + i * 145;
        canvas.drawOval(
          Rect.fromCenter(center: Offset(x, 660), width: 43, height: 60),
          Paint()..color = const Color(0xFF080909).withOpacity(0.84),
        );
      }
    } else if (isAfrica) {
      // Stylized African savannah, baobab-like tree, and sunset.
      canvas.drawCircle(
        const Offset(525, 405),
        76,
        Paint()..color = gold.withOpacity(0.15),
      );
      final distantHill = Path()
        ..moveTo(0, 625)
        ..quadraticBezierTo(180, 520, 350, 630)
        ..quadraticBezierTo(530, 560, 720, 610)
        ..lineTo(720, 850)
        ..lineTo(0, 850)
        ..close();
      canvas.drawPath(
        distantHill,
        Paint()..color = const Color(0xFF11130F).withOpacity(0.75),
      );
      // Trunk and spreading canopy.
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          const Rect.fromLTWH(150, 440, 38, 245),
          const Radius.circular(8),
        ),
        silhouettePaint,
      );
      final branches = Paint()
        ..color = const Color(0xFF090B0A).withOpacity(0.9)
        ..strokeWidth = 19
        ..strokeCap = StrokeCap.round;
      canvas.drawLine(const Offset(168, 490), const Offset(105, 420), branches);
      canvas.drawLine(const Offset(168, 480), const Offset(235, 405), branches);
      canvas.drawLine(const Offset(168, 510), const Offset(75, 485), branches);
      canvas.drawLine(const Offset(168, 505), const Offset(265, 470), branches);
      for (final leaf in [
        const Rect.fromLTWH(65, 365, 100, 90),
        const Rect.fromLTWH(125, 330, 115, 100),
        const Rect.fromLTWH(200, 355, 90, 90),
      ]) {
        canvas.drawOval(leaf, silhouettePaint);
      }
    } else if (isAncient) {
      // Monumental columns and a classical pediment.
      final pediment = Path()
        ..moveTo(105, 465)
        ..lineTo(360, 350)
        ..lineTo(615, 465)
        ..close();
      canvas.drawPath(
        pediment,
        Paint()..color = const Color(0xFF090A0B).withOpacity(0.85),
      );
      canvas.drawPath(pediment, detailPaint);
      for (var i = 0; i < 5; i++) {
        final x = 145.0 + i * 108;
        canvas.drawRect(
          Rect.fromLTWH(x, 465, 57, 210),
          Paint()..color = const Color(0xFF090A0B).withOpacity(0.85),
        );
        canvas.drawRect(
          Rect.fromLTWH(x - 7, 460, 71, 14),
          Paint()..color = gold.withOpacity(0.22),
        );
        canvas.drawLine(
          Offset(x + 9, 485),
          Offset(x + 9, 660),
          detailPaint..color = pale.withOpacity(0.13),
        );
      }
      canvas.drawRect(
        const Rect.fromLTWH(120, 675, 480, 18),
        Paint()..color = const Color(0xFF080909).withOpacity(0.9),
      );
    } else {
      // General historical scene: distant mountains, rising sun and architecture.
      final mountains = Path()
        ..moveTo(0, 620)
        ..lineTo(125, 455)
        ..lineTo(235, 575)
        ..lineTo(375, 405)
        ..lineTo(510, 565)
        ..lineTo(610, 465)
        ..lineTo(720, 590)
        ..lineTo(720, 830)
        ..lineTo(0, 830)
        ..close();
      canvas.drawPath(
        mountains,
        Paint()..color = const Color(0xFF0A0C0E).withOpacity(0.78),
      );
      canvas.drawCircle(
        const Offset(360, 480),
        66,
        Paint()..color = gold.withOpacity(0.10),
      );
      canvas.drawLine(
        const Offset(75, 720),
        const Offset(645, 720),
        Paint()
          ..color = gold.withOpacity(0.28)
          ..strokeWidth = 2,
      );
    }

    // A fine, restrained frame gives the scene a premium editorial finish.
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(35, 35, 650, 1210),
        const Radius.circular(25),
      ),
      Paint()
        ..color = gold.withOpacity(0.42)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );

    // Deterministic fine particles create atmosphere without random flicker.
    for (var i = 0; i < 44; i++) {
      final x = ((i * 137 + sceneNumber * 41) % 680 + 20).toDouble();
      final y = ((i * 211 + sceneNumber * 67) % 760 + 170).toDouble();
      final radius = 1.0 + (i % 3) * 0.55;
      canvas.drawCircle(
        Offset(x, y),
        radius,
        Paint()..color = gold.withOpacity(0.08 + (i % 4) * 0.025),
      );
    }

    void drawText(
      String text,
      double top,
      double fontSize,
      Color color, {
      FontWeight weight = FontWeight.w500,
      int maxLines = 3,
      double maxWidth = 570,
      double letterSpacing = 0,
    }) {
      final painter = TextPainter(
        text: TextSpan(
          text: text,
          style: TextStyle(
            color: color,
            fontSize: fontSize,
            fontWeight: weight,
            height: 1.25,
            letterSpacing: letterSpacing,
            shadows: [
              Shadow(
                color: Colors.black.withOpacity(0.6),
                blurRadius: 12,
                offset: const Offset(0, 3),
              ),
            ],
          ),
        ),
        textDirection: TextDirection.ltr,
        textAlign: TextAlign.center,
        maxLines: maxLines,
        ellipsis: '…',
      )..layout(maxWidth: maxWidth);

      painter.paint(
        canvas,
        Offset((width - painter.width) / 2, top),
      );
    }

    drawText(
      'CHRONICLE AI',
      112,
      25,
      gold,
      weight: FontWeight.w800,
      letterSpacing: 5,
    );
    drawText(
      'BRING THE PAST TO LIFE',
      160,
      14,
      muted,
      letterSpacing: 2.4,
    );

    canvas.drawLine(
      const Offset(260, 225),
      const Offset(460, 225),
      Paint()
        ..color = gold.withOpacity(0.82)
        ..strokeWidth = 2,
    );

    drawText(
      'CHAPTER ${sceneNumber.toString().padLeft(2, '0')}'
      '  /  ${totalScenes.toString().padLeft(2, '0')}',
      250,
      17,
      gold,
      weight: FontWeight.w700,
      letterSpacing: 2,
    );

    // Readability panel behind the chapter title.
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(65, 350, 590, 255),
        const Radius.circular(22),
      ),
      Paint()..color = const Color(0xB908090A),
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(65, 350, 590, 255),
        const Radius.circular(22),
      ),
      Paint()
        ..color = gold.withOpacity(0.24)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1,
    );

    drawText(
      sceneTitle,
      405,
      40,
      Colors.white,
      weight: FontWeight.w800,
      maxLines: 5,
      maxWidth: 535,
    );

    canvas.drawLine(
      const Offset(275, 650),
      const Offset(445, 650),
      Paint()
        ..color = gold.withOpacity(0.85)
        ..strokeWidth = 2,
    );

    drawText(
      projectTitle,
      720,
      23,
      pale,
      weight: FontWeight.w600,
      maxLines: 3,
      maxWidth: 550,
    );

    drawText(
      'HISTORY  •  STORY  •  LEGACY',
      1080,
      15,
      muted,
      letterSpacing: 2,
    );

    drawText(
      'CHRONICLE AI',
      1150,
      17,
      gold,
      weight: FontWeight.w700,
      letterSpacing: 3,
    );

    final picture = recorder.endRecording();
    final image = await picture.toImage(width, height);

    try {
      final bytes = await image.toByteData(
        format: ui.ImageByteFormat.png,
      );
      if (bytes == null) {
        throw Exception('Could not encode a scene image.');
      }
      await file.writeAsBytes(
        bytes.buffer.asUint8List(),
        flush: true,
      );
    } finally {
      image.dispose();
    }
  }
'''

# All checks occur before the source is written.
backup = Path(
    "backups/video_exporter_before_cinematic_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".dart"
)

updated = source[:start] + new_function.rstrip() + "\n}"

if updated == source:
    raise SystemExit("STOP: No renderer changes detected.")

backup.write_text(source)
renderer.write_text(updated)

print("Cinematic scene renderer updated.")
print(f"Original renderer backed up to: {backup}")
print("Preserved existing export pipeline, duration handling and ambient audio.")
