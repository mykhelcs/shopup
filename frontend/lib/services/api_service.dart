import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiService {
  // Dynamically determine baseUrl based on platform
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    } else if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    } else {
      // iOS Simulator and others
      return 'http://localhost:8000';
    }
  }

  // Verify Firebase token with backend
  Future<Map<String, dynamic>> verifyToken(String idToken) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/verify'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $idToken',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Token verification failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to verify token: $e');
    }
  }

  // Get user profile from backend
  Future<Map<String, dynamic>> getUserProfile(String idToken) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/users/me'),
        headers: {
          'Authorization': 'Bearer $idToken',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get user profile: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get user profile: $e');
    }
  }

  // Get products (guest or authenticated)
  Future<List<dynamic>> getProducts({String? idToken}) async {
    try {
      final headers = <String, String>{};
      if (idToken != null) {
        headers['Authorization'] = 'Bearer $idToken';
      }

      final response = await http.get(
        Uri.parse('$baseUrl/products'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get products: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get products: $e');
    }
  }

  // Get categories
  Future<List<dynamic>> getCategories({String? idToken}) async {
    try {
      final headers = <String, String>{};
      if (idToken != null) {
        headers['Authorization'] = 'Bearer $idToken';
      }

      final response = await http.get(
        Uri.parse('$baseUrl/categories'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get categories: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get categories: $e');
    }
  }
}
