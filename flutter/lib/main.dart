import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/cart_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/buyer/home_screen.dart';
import 'screens/seller/seller_dashboard_screen.dart';
import 'services/database_helper.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Test database connection
  final dbHelper = DatabaseHelper();
  final isConnected = await dbHelper.testConnection();
  print('\n=== Database Connection Test ===');
  print('Database connection ${isConnected ? 'successful' : 'failed'}');
  if (!isConnected) {
    print('WARNING: Database connection failed. Please check your database configuration.');
  }

  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProxyProvider<AuthProvider, CartProvider>(
          create: (_) => CartProvider(),
          update: (_, auth, cart) {
            if (auth.isAuthenticated && auth.currentUser != null) {
              cart?.loadCartItems(auth.currentUser!['Buyer_ID'].toString());
            }
            return cart ?? CartProvider();
          },
        ),
      ],
      child: MaterialApp(
        title: 'Fenamaz',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
          appBarTheme: AppBarTheme(
            elevation: 0,
            backgroundColor: Colors.white,
            foregroundColor: Colors.black,
            iconTheme: IconThemeData(color: Colors.black),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          ),
          cardTheme: CardTheme(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        initialRoute: '/login',
        onGenerateRoute: (settings) {
          print('Navigating to: ${settings.name}');
          switch (settings.name) {
            case '/login':
              return MaterialPageRoute(builder: (_) => LoginScreen());
            case '/buyer/home':
              return MaterialPageRoute(builder: (_) => HomeScreen());
            case '/seller/dashboard':
              return MaterialPageRoute(builder: (_) => SellerDashboardScreen());
            case '/admin/dashboard':
              return MaterialPageRoute(
                builder: (_) => Scaffold(
                  appBar: AppBar(
                    title: Text('Admin Dashboard'),
                    actions: [
                      IconButton(
                        icon: Icon(Icons.logout),
                        onPressed: () {
                          Provider.of<AuthProvider>(_, listen: false).logout();
                          Navigator.pushReplacementNamed(_, '/login');
                        },
                      ),
                    ],
                  ),
                  body: Center(child: Text('Admin Dashboard')),
                ),
              );
            default:
              return MaterialPageRoute(builder: (_) => LoginScreen());
          }
        },
      ),
    );
  }
} 