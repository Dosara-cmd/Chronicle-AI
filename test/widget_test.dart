import 'package:flutter_test/flutter_test.dart';
import 'package:chronicle_ai/main.dart';

void main() {
  testWidgets('Chronicle AI displays both generators', (tester) async {
    await tester.pumpWidget(const ChronicleAI());

    expect(find.text('CHRONICLE AI'), findsOneWidget);
    expect(find.text('Automatic AI Generator'), findsOneWidget);
    expect(find.text('Paste AI Generator'), findsOneWidget);
  });
}
