import 'package:mysql1/mysql1.dart';
import 'dart:io';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  DatabaseHelper._internal();

  MySqlConnection? _connection;
  bool _isConnected = false;

  // Configuration options to try
  final List<Map<String, dynamic>> _connectionConfigs = [
    {
      'host': 'localhost',
      'port': 3306,
      'user': 'root',
      'password': '',
      'db': 'fenamaz',
    },
    {
      'host': '127.0.0.1',
      'port': 3306,
      'user': 'root',
      'password': '',
      'db': 'fenamaz',
    },
    {
      'host': '::1',  // IPv6 localhost
      'port': 3306,
      'user': 'root',
      'password': '',
      'db': 'fenamaz',
    },
    {
      'host': 'localhost',
      'port': 3307,  // Alternative port
      'user': 'root',
      'password': '',
      'db': 'fenamaz',
    }
  ];

  Future<bool> testConnection() async {
    try {
      print('\n=== Testing Database Connection ===');
      
      // Simple connection test with increased timeout
      final settings = ConnectionSettings(
        host: 'localhost',
        port: 3306,
        user: 'root',
        password: '',
        db: 'fenamaz',
        timeout: Duration(seconds: 60),
      );

      print('Attempting connection with settings:');
      print('Host: ${settings.host}');
      print('Port: ${settings.port}');
      print('Database: ${settings.db}');
      print('User: ${settings.user}');
      
      final testConn = await MySqlConnection.connect(settings);
      print('Basic connection successful');
      
      // Test if we can query
      final result = await testConn.query('SELECT 1');
      print('Query test successful');
      
      await testConn.close();
      return true;
    } catch (e) {
      print('Connection test failed: $e');
      if (e is SocketException) {
        print('Socket error - MySQL might not be running');
        print('Error details: ${e.message}');
      }
      return false;
    }
  }

  Future<MySqlConnection> get connection async {
    try {
      if (_connection != null && _isConnected) {
        // Test existing connection
        await _connection!.query('SELECT 1');
        return _connection!;
      }
    } catch (e) {
      _connection = null;
      _isConnected = false;
    }

    try {
      final settings = ConnectionSettings(
        host: 'localhost',
        port: 3306,
        user: 'root',
        password: '',
        db: 'fenamaz',
        timeout: Duration(seconds: 60),
      );

      _connection = await MySqlConnection.connect(settings);
      _isConnected = true;
      return _connection!;
    } catch (e) {
      print('Failed to connect to database: $e');
      if (e is SocketException) {
        throw Exception('MySQL is not running. Please start MySQL in XAMPP Control Panel.');
      }
      throw Exception('Database connection failed: ${e.toString()}');
    }
  }

  Future<void> closeConnection() async {
    if (_connection != null) {
      try {
        await _connection!.close();
        _connection = null;
        _isConnected = false;
      } catch (e) {
        print('Error closing connection: $e');
      }
    }
  }

  // Admin Account Operations
  Future<Results> createAdminAccount(Map<String, dynamic> adminData) async {
    final conn = await connection;
    return await conn.query(
      'INSERT INTO admin_accounts (Firstname, Middle_Initial, Lastname, Suffix, Email, Password, Status, Role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [
        adminData['Firstname'],
        adminData['Middle_Initial'],
        adminData['Lastname'],
        adminData['Suffix'],
        adminData['Email'],
        adminData['Password'],
        adminData['Status'],
        adminData['Role'],
      ],
    );
  }

  // Buyer Account Operations
  Future<Results> createBuyerAccount(Map<String, dynamic> buyerData) async {
    final conn = await connection;
    return await conn.query(
      'INSERT INTO buyer_accounts (Personal_ID, Address_ID, Valid_ID, Phone, Email, Password, Profile_Pic, Status, Role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [
        buyerData['Personal_ID'],
        buyerData['Address_ID'],
        buyerData['Valid_ID'],
        buyerData['Phone'],
        buyerData['Email'],
        buyerData['Password'],
        buyerData['Profile_Pic'],
        buyerData['Status'],
        buyerData['Role'],
      ],
    );
  }

  // Seller Account Operations
  Future<Results> createSellerAccount(Map<String, dynamic> sellerData) async {
    final conn = await connection;
    return await conn.query(
      'INSERT INTO seller_accounts (Personal_ID, Address_ID, Valid_ID, Business_ID, Phone, Email, Password, Status, Role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [
        sellerData['Personal_ID'],
        sellerData['Address_ID'],
        sellerData['Valid_ID'],
        sellerData['Business_ID'],
        sellerData['Phone'],
        sellerData['Email'],
        sellerData['Password'],
        sellerData['Status'],
        sellerData['Role'],
      ],
    );
  }

  // Product Operations
  Future<Results> createProduct(Map<String, dynamic> productData) async {
    final conn = await connection;
    return await conn.query(
      'INSERT INTO products (Seller_ID, Product_Info_ID, Product_Category, Total_Stocks, Status) VALUES (?, ?, ?, ?, ?)',
      [
        productData['Seller_ID'],
        productData['Product_Info_ID'],
        productData['Product_Category'],
        productData['Total_Stocks'],
        productData['Status'],
      ],
    );
  }

  // Order Operations
  Future<Results> createOrder(Map<String, dynamic> orderData) async {
    final conn = await connection;
    return await conn.query(
      'INSERT INTO buyer_orders (Product_ID, Seller_ID, Shop_ID, Buyer_ID, Quantity, Total_Amount, Payment_Method, Payment_Status, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [
        orderData['Product_ID'],
        orderData['Seller_ID'],
        orderData['Shop_ID'],
        orderData['Buyer_ID'],
        orderData['Quantity'],
        orderData['Total_Amount'],
        orderData['Payment_Method'],
        orderData['Payment_Status'],
        orderData['Status'],
      ],
    );
  }

  // Authentication Methods
  Future<Map<String, dynamic>?> authenticateUser(String email, String password, String userType) async {
    try {
      print('\n--- Starting Authentication ---');
      print('User Type: $userType');
      print('Email: $email');
      
      final conn = await connection;
      String table;
      String idColumn;
      
      switch (userType.toLowerCase()) {
        case 'admin':
          table = 'admin_accounts';
          idColumn = 'Admin_ID';
          print('Authenticating as admin');
          break;
        case 'buyer':
          table = 'buyer_accounts';
          idColumn = 'Buyer_ID';
          print('Authenticating as buyer');
          break;
        case 'seller':
          table = 'seller_accounts';
          idColumn = 'Seller_ID';
          print('Authenticating as seller');
          break;
        default:
          throw Exception('Invalid user type: $userType');
      }

      // First check if the email exists
      print('Checking if email exists...');
      final emailCheck = await conn.query(
        'SELECT Email FROM $table WHERE BINARY Email = ?',
        [email]
      );
      
      if (emailCheck.isEmpty) {
        print('Email not found in $table');
        return null;
      }
      print('Email found in database');

      // Then try to authenticate with exact password match
      print('Attempting full authentication...');
      final query = 'SELECT * FROM $table WHERE BINARY Email = ? AND BINARY Password = ?';
      print('Executing query: $query');
      print('Parameters: Email=$email');
      
      final results = await conn.query(query, [email, password]);
      print('Query executed successfully');
      print('Found ${results.length} matching records');

      if (results.isEmpty) {
        print('No matching user found with provided credentials');
        return null;
      }

      final user = results.first;
      print('User authenticated successfully');
      print('User ID: ${user[idColumn]}');
      print('User Email: ${user['Email']}');
      print('User Status: ${user['Status']}');
      
      // Verify the data matches exactly
      if (user['Email'] != email || user['Password'] != password) {
        print('Credential mismatch - exact comparison failed');
        return null;
      }

      return results.first.fields;
    } catch (e) {
      print('Authentication error occurred: $e');
      print('Stack trace: ${StackTrace.current}');
      throw Exception('Authentication failed: $e');
    }
  }

  // Product Methods
  Future<List<Map<String, dynamic>>> getProducts() async {
    final conn = await connection;
    var results = await conn.query('''
      SELECT p.*, pi.image_url, ps.stock_quantity 
      FROM products p
      LEFT JOIN product_image pi ON p.product_id = pi.product_id
      LEFT JOIN product_stock ps ON p.product_id = ps.product_id
    ''');
    
    return results.map((row) => {
      'id': row['product_id'],
      'name': row['product_name'],
      'description': row['description'],
      'price': row['price'],
      'image_url': row['image_url'],
      'stock': row['stock_quantity'],
    }).toList();
  }

  // Cart Methods
  Future<List<Map<String, dynamic>>> getCartItems(String buyerId) async {
    final conn = await connection;
    var results = await conn.query('''
      SELECT bc.*, p.product_name, p.price, pi.image_url 
      FROM buyer_cart bc
      JOIN products p ON bc.product_id = p.product_id
      LEFT JOIN product_image pi ON p.product_id = pi.product_id
      WHERE bc.buyer_id = ?
    ''', [buyerId]);
    
    return results.map((row) => {
      'id': row['cart_id'],
      'product_id': row['product_id'],
      'quantity': row['quantity'],
      'name': row['product_name'],
      'price': row['price'],
      'image_url': row['image_url'],
    }).toList();
  }

  Future<void> addToCart(String buyerId, int productId, int quantity) async {
    final conn = await connection;
    await conn.query('''
      INSERT INTO buyer_cart (buyer_id, product_id, quantity) 
      VALUES (?, ?, ?)
      ON DUPLICATE KEY UPDATE quantity = quantity + ?
    ''', [buyerId, productId, quantity, quantity]);
  }

  Future<void> updateCartQuantity(String buyerId, int productId, int quantity) async {
    final conn = await connection;
    if (quantity <= 0) {
      await conn.query(
        'DELETE FROM buyer_cart WHERE buyer_id = ? AND product_id = ?',
        [buyerId, productId]
      );
    } else {
      await conn.query(
        'UPDATE buyer_cart SET quantity = ? WHERE buyer_id = ? AND product_id = ?',
        [quantity, buyerId, productId]
      );
    }
  }

  // User Profile Methods
  Future<Map<String, dynamic>> getBuyerProfile(String buyerId) async {
    final conn = await connection;
    var personalInfo = await conn.query(
      'SELECT * FROM buyer_personal_info WHERE buyer_id = ?',
      [buyerId]
    );
    
    var addressInfo = await conn.query(
      'SELECT * FROM buyer_address_info WHERE buyer_id = ?',
      [buyerId]
    );

    if (personalInfo.isNotEmpty) {
      var profile = personalInfo.first;
      var address = addressInfo.isNotEmpty ? addressInfo.first : null;
      
      return {
        'id': profile['buyer_id'],
        'name': '${profile['first_name']} ${profile['last_name']}',
        'email': profile['email'],
        'phone': profile['contact_number'],
        'address': address != null ? '${address['street']}, ${address['city']}, ${address['state']}' : null,
      };
    }
    throw Exception('User not found');
  }

  Future<Map<String, dynamic>> getSellerProfile(String sellerId) async {
    final conn = await connection;
    var personalInfo = await conn.query(
      'SELECT * FROM seller_personal_info WHERE seller_id = ?',
      [sellerId]
    );
    
    var shopInfo = await conn.query(
      'SELECT * FROM seller_shop_info WHERE seller_id = ?',
      [sellerId]
    );

    if (personalInfo.isNotEmpty) {
      var profile = personalInfo.first;
      var shop = shopInfo.isNotEmpty ? shopInfo.first : null;
      
      return {
        'id': profile['seller_id'],
        'name': '${profile['first_name']} ${profile['last_name']}',
        'email': profile['email'],
        'phone': profile['contact_number'],
        'shop_name': shop?['shop_name'],
        'shop_description': shop?['description'],
      };
    }
    throw Exception('Seller not found');
  }

  Future<String?> checkDatabaseConfiguration() async {
    try {
      print('\n=== Checking Database Configuration ===');
      
      // Check if XAMPP is running
      try {
        final socket = await Socket.connect('localhost', 3306, timeout: Duration(seconds: 5));
        await socket.close();
        print('MySQL port 3306 is accessible');
      } catch (e) {
        print('MySQL port 3306 is not accessible');
        return 'MySQL is not running. Please start MySQL in XAMPP Control Panel.';
      }

      // Try to connect without database to check MySQL access
      try {
        final settings = ConnectionSettings(
          host: 'localhost',
          port: 3306,
          user: 'root',
          password: '',
        );
        final conn = await MySqlConnection.connect(settings);
        await conn.close();
        print('MySQL root access verified');
      } catch (e) {
        print('MySQL root access failed: $e');
        return 'Cannot connect to MySQL. Please check if root password is correct.';
      }

      // Check if database exists
      try {
        final settings = ConnectionSettings(
          host: 'localhost',
          port: 3306,
          user: 'root',
          password: '',
          db: 'fenamaz',
        );
        final conn = await MySqlConnection.connect(settings);
        final results = await conn.query('SHOW TABLES');
        print('Found ${results.length} tables in fenamaz database');
        if (results.isEmpty) {
          return 'Database "fenamaz" exists but has no tables. Please import the database structure.';
        }
        await conn.close();
      } catch (e) {
        print('Database check failed: $e');
        if (e.toString().contains('Unknown database')) {
          return 'Database "fenamaz" does not exist. Please create it in phpMyAdmin.';
        }
        return 'Cannot access database. Error: ${e.toString()}';
      }

      return null; // No issues found
    } catch (e) {
      print('Configuration check failed: $e');
      return 'Database configuration check failed: ${e.toString()}';
    }
  }
} 