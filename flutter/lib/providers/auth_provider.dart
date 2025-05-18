import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/database_helper.dart';

class AuthProvider with ChangeNotifier {
  final DatabaseHelper _db = DatabaseHelper();
  final _storage = FlutterSecureStorage();
  Map<String, dynamic>? _currentUser;
  String? _userType;
  bool _isAuthenticated = false;

  Map<String, dynamic>? get currentUser => _currentUser;
  String? get userType => _userType;
  bool get isAuthenticated => _isAuthenticated;

  Future<bool> login(String email, String password, String userType) async {
    try {
      print('\n=== Login Attempt ===');
      print('Email: $email');
      print('User Type: $userType');
      
      // Validate inputs
      if (email.isEmpty || password.isEmpty) {
        print('Login failed: Empty email or password');
        return false;
      }

      print('Attempting database authentication...');
      final user = await _db.authenticateUser(email, password, userType);
      
      if (user != null) {
        print('Database authentication successful');
        print('User data received: ${user.toString()}');
        
        _currentUser = user;
        _userType = userType;
        _isAuthenticated = true;
        
        print('Storing credentials securely...');
        await _storage.write(key: 'user_type', value: userType);
        await _storage.write(key: 'email', value: email);
        print('Credentials stored successfully');
        
        print('Notifying listeners of successful login');
        notifyListeners();
        return true;
      }
      
      print('Login failed: Invalid credentials');
      return false;
    } catch (e) {
      print('Login error occurred: $e');
      print('Stack trace: ${StackTrace.current}');
      return false;
    }
  }

  Future<void> logout() async {
    try {
      print('\n=== Logout Attempt ===');
      _currentUser = null;
      _userType = null;
      _isAuthenticated = false;
      
      print('Clearing secure storage...');
      await _storage.deleteAll();
      print('Secure storage cleared');
      
      print('Notifying listeners of logout');
      notifyListeners();
    } catch (e) {
      print('Logout error: $e');
      print('Stack trace: ${StackTrace.current}');
      throw Exception('Logout failed: $e');
    }
  }

  Future<bool> checkAuthStatus() async {
    try {
      print('\n=== Checking Auth Status ===');
      final userType = await _storage.read(key: 'user_type');
      final email = await _storage.read(key: 'email');
      
      print('Stored user type: $userType');
      print('Stored email: $email');
      
      if (userType != null && email != null) {
        print('Found stored credentials');
        _userType = userType;
        _isAuthenticated = true;
        notifyListeners();
        return true;
      }
      
      print('No stored credentials found');
      return false;
    } catch (e) {
      print('Auth status check error: $e');
      print('Stack trace: ${StackTrace.current}');
      return false;
    }
  }
} 