import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'auth_service.dart';
import 'api_service.dart';
import 'firestore_service.dart';
import 'dart:async';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final ApiService _apiService = ApiService();
  final FirestoreService _firestoreService = FirestoreService();

  User? _user;
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _userProfile;
  StreamSubscription? _profileSubscription;

  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  Map<String, dynamic>? get userProfile => _userProfile;
  bool get isAuthenticated => _user != null;

  AuthProvider() {
    // Listen to auth state changes
    _authService.authStateChanges.listen((User? user) {
      _user = user;
      if (user != null) {
        _loadUserProfile();
        _listenToProfileChanges(user.uid);
      } else {
        _userProfile = null;
        _profileSubscription?.cancel();
      }
      notifyListeners();
    });
  }

  void _listenToProfileChanges(String uid) {
    _profileSubscription?.cancel();
    _profileSubscription = _firestoreService.getUserProfileStream(uid).listen((snapshot) {
      if (snapshot.exists) {
        _userProfile = snapshot.data() as Map<String, dynamic>?;
        notifyListeners();
      }
    });
  }

  // Update user profile in Firestore
  Future<void> updateProfile(Map<String, dynamic> data) async {
    if (_user != null) {
      await _firestoreService.updateUserProfile(_user!.uid, data);
    }
  }

  // Load user profile from backend
  Future<void> _loadUserProfile() async {
    try {
      final token = await _authService.getIdToken();
      if (token != null) {
        _userProfile = await _apiService.getUserProfile(token);
        notifyListeners();
      }
    } catch (e) {
      // Silent fail - profile loading is not critical
      debugPrint('Failed to load user profile: $e');
    }
  }

  // Sign in with email and password
  Future<bool> signIn(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final credential = await _authService.signInWithEmail(email, password);
      _user = credential.user;

      // Try to verify token with backend (optional - won't fail auth if backend is down)
      try {
        final token = await _authService.getIdToken();
        if (token != null) {
          await _apiService.verifyToken(token);
          await _loadUserProfile();
        }
      } catch (e) {
        debugPrint('Backend verification failed (non-critical): $e');
        // Continue anyway - Firebase auth succeeded
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Register with email and password
  Future<bool> register(String email, String password, String username) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      debugPrint('Attempting to register user: $email');
      final credential = await _authService.registerWithEmail(email, password);
      _user = credential.user;
      debugPrint('Firebase Auth success: ${_user?.uid}');

      if (_user != null) {
        try {
          debugPrint('Attempting to write user data to Firestore...');
          // Write initial user data to Firestore
          await _firestoreService.writeUserDataToFirestore(
            _user!.uid, 
            username, 
            email
          );
          debugPrint('Firestore data written successfully');
        } catch (e) {
          _errorMessage = 'Firestore Error: $e';
          debugPrint('Firestore write failure: $e');
          _isLoading = false;
          notifyListeners();
          return false;
        }
      }

      // Try to verify token with backend (optional - won't fail auth if backend is down)
      try {
        debugPrint('Attempting backend token verification...');
        final token = await _authService.getIdToken();
        if (token != null) {
          await _apiService.verifyToken(token);
          await _loadUserProfile();
          debugPrint('Backend verification success');
        }
      } catch (e) {
        debugPrint('Backend verification failed (non-critical): $e');
        // Continue anyway - Firebase auth succeeded
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      // This catches errors from _authService.registerWithEmail
      _errorMessage = e.toString();
      debugPrint('Registration catch block: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Sign out
  Future<void> signOut() async {
    await _authService.signOut();
    _user = null;
    _userProfile = null;
    notifyListeners();
  }

  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
