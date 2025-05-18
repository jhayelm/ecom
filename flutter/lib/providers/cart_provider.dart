import 'package:flutter/foundation.dart';
import '../services/database_helper.dart';

class CartProvider with ChangeNotifier {
  final DatabaseHelper _db = DatabaseHelper();
  List<Map<String, dynamic>> _items = [];
  bool _isLoading = false;
  String? _error;

  List<Map<String, dynamic>> get items => _items;
  bool get isLoading => _isLoading;
  String? get error => _error;

  double get total {
    return _items.fold(0, (sum, item) => 
      sum + ((item['price'] ?? 0) * (item['quantity'] ?? 0)));
  }

  Future<void> loadCartItems(String buyerId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      _items = await _db.getCartItems(buyerId);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addToCart(String buyerId, int productId, int quantity) async {
    try {
      await _db.addToCart(buyerId, productId, quantity);
      await loadCartItems(buyerId);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> updateQuantity(String buyerId, int productId, int quantity) async {
    try {
      await _db.updateCartQuantity(buyerId, productId, quantity);
      await loadCartItems(buyerId);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> removeFromCart(String buyerId, int productId) async {
    try {
      await _db.updateCartQuantity(buyerId, productId, 0); // 0 quantity will remove the item
      await loadCartItems(buyerId);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> clearCart(String buyerId) async {
    try {
      // TODO: Implement clear cart in DatabaseHelper
      _items = [];
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
} 