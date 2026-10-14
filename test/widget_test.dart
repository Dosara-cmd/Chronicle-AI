import 'package:flutter_test/flutter_test.dart';
import 'package:chronicle_ai/main.dart';

void main() {
  testWidgets('Chronicle AI home screen loads', (tester) async {
    await tester.pumpWidget(const ChronicleAI());
    await tester.pumpAndSettle();

    expect(find.text('CHRONICLE AI'), findsWidgets);
    expect(find.text('Automatic AI Generator'), findsWidgets);
    expect(find.text('Paste AI Generator'), findsWidgets);
  });
}
