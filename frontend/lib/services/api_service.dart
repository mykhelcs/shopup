import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // TODO: Update this to your actual backend URL
  // For Android emulator: http://10.0.2.2:8000
  // For iOS simulator: http://localhost:8000
  // For physical device: http://YOUR_IP:8000
  static const String baseUrl = 'http://10.0.2.2:8000';

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
