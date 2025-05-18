import 'package:flutter/foundation.dart';

class CartItem {
  final String id;
  final String name;
  final String category;
  final double price;
  final String image;
  int quantity;

  CartItem({
    required this.id,
    required this.name,
    required this.category,
    required this.price,
    required this.image,
    this.quantity = 1,
  });
}

class CartService extends ChangeNotifier {
  final Map<String, CartItem> _items = {};

  Map<String, CartItem> get items => {..._items};

  int get itemCount => _items.length;

  double get totalAmount {
    return _items.values.fold(0.0, (sum, item) => sum + (item.price * item.quantity));
  }

  void addItem({
    required String id,
    required String name,
    required String category,
    required double price,
    required String image,
  }) {
    if (_items.containsKey(id)) {
      _items.update(
        id,
        (existingItem) => CartItem(
          id: existingItem.id,
          name: existingItem.name,
          category: existingItem.category,
          price: existingItem.price,
          image: existingItem.image,
          quantity: existingItem.quantity + 1,
        ),
      );
    } else {
      _items.putIfAbsent(
        id,
        () => CartItem(
          id: id,
          name: name,
          category: category,
          price: price,
          image: image,
        ),
      );
    }
    notifyListeners();
  }

  void removeItem(String id) {
    _items.remove(id);
    notifyListeners();
  }

  void updateQuantity(String id, int quantity) {
    if (_items.containsKey(id)) {
      if (quantity <= 0) {
        removeItem(id);
      } else {
        _items.update(
          id,
          (existingItem) => CartItem(
            id: existingItem.id,
            name: existingItem.name,
            category: existingItem.category,
            price: existingItem.price,
            image: existingItem.image,
            quantity: quantity,
          ),
        );
        notifyListeners();
      }
    }
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
} 