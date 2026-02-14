import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';

class FirestoreService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  Future<void> writeUserDataToFirestore(String userId, String username, String email) async {
    try {
      await _db.collection('users').doc(userId).set({
        'username': username,
        'email': email,
        'full_name': username, // Use username as initial full_name
        'created_at': FieldValue.serverTimestamp(),
        'last_updated': FieldValue.serverTimestamp(),
      });
      debugPrint("User data written to Firestore successfully for userId: $userId");
    } catch (e) {
      debugPrint("Failed to write user data to Firestore: $e");
      rethrow;
    }
  }

  // Stream of user data
  Stream<DocumentSnapshot> getUserProfileStream(String uid) {
    return _db.collection('users').doc(uid).snapshots();
  }

  // Update user profile
  Future<void> updateUserProfile(String uid, Map<String, dynamic> data) {
    return _db.collection('users').doc(uid).set(data, SetOptions(merge: true));
  }

  // Get current user profile once
  Future<DocumentSnapshot> getUserProfile(String uid) {
    return _db.collection('users').doc(uid).get();
  }
}
