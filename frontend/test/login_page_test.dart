import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:smartbez/presentation/screens/auth/login_page.dart';
import 'package:smartbez/services/auth_provider.dart' as provider;
import 'package:firebase_auth/firebase_auth.dart';

// Simple manual mock for AuthProvider
class MockAuthProvider extends ChangeNotifier implements provider.AuthProvider {
  @override
  bool isLoading = false;
  @override
  String? errorMessage;
  @override
  User? user;
  @override
  Map<String, dynamic>? userProfile;
  @override
  bool get isAuthenticated => user != null;

  @override
  Future<bool> signIn(String email, String password) async => true;
  @override
  Future<bool> register(String email, String password, String username) async => true;
  @override
  Future<void> signOut() async {}
  @override
  void clearError() {}
  @override
  Future<void> updateProfile(Map<String, dynamic> data) async {}
  @override
  Future<bool> signInWithGoogle() async => true;
  @override
  Future<bool> signInWithFacebook() async => true;

  @override
  void addListener(VoidCallback listener) => super.addListener(listener);
  @override
  void removeListener(VoidCallback listener) => super.removeListener(listener);
  @override
  void dispose() => super.dispose();
  @override
  bool get hasListeners => super.hasListeners;
  @override
  void notifyListeners() => super.notifyListeners();
}

void main() {
  testWidgets('LoginPage shows Social Login buttons', (WidgetTester tester) async {
    final mockAuth = MockAuthProvider();

    // Set a larger physical size for the test
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 1.0;

    await tester.pumpWidget(
      ChangeNotifierProvider<provider.AuthProvider>.value(
        value: mockAuth,
        child: const MaterialApp(
          home: LoginPage(),
        ),
      ),
    );

    // Pump instead of pumpAndSettle to avoid Image.network timeout
    await tester.pump(const Duration(seconds: 2));

    // Verify "OR" divider exists
    expect(find.textContaining('OR'), findsOneWidget);

    // Verify Google and Facebook buttons exist
    expect(find.textContaining('Google'), findsOneWidget);
    expect(find.textContaining('Facebook'), findsOneWidget);

    // Verify Google and Facebook buttons exist
    expect(find.text('Google'), findsOneWidget);
    expect(find.text('Facebook'), findsOneWidget);
    
    // Verify icons/images (Google uses NetworkImage/Image.network in our code)
    expect(find.byType(Image), findsOneWidget); // Google logo
    expect(find.byIcon(Icons.facebook), findsOneWidget); // Facebook icon
  });
}
