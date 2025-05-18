import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/cart_provider.dart';
import 'cart_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    
    final List<Widget> _screens = [
      ProductListView(),
      CartScreen(),
      Center(child: Text('Profile Screen')), // Replace with actual ProfileScreen
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(_selectedIndex == 0 ? 'Fenamaz Shop' : 
                    _selectedIndex == 1 ? 'Shopping Cart' : 'Profile'),
        actions: [
          if (_selectedIndex == 0) IconButton(
            icon: Icon(Icons.search),
            onPressed: () {
              // TODO: Implement search
            },
          ),
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () async {
              await authProvider.logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: 'Cart',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class ProductListView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer2<CartProvider, AuthProvider>(
      builder: (context, cartProvider, authProvider, child) {
        if (authProvider.currentUser == null) {
          return Center(child: Text('Please log in to view products'));
        }

        return Column(
          children: [
            // Categories horizontal list
            Container(
              height: 100,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: EdgeInsets.all(8),
                children: [
                  _buildCategoryItem(context, 'All', Icons.apps),
                  _buildCategoryItem(context, 'Electronics', Icons.devices),
                  _buildCategoryItem(context, 'Fashion', Icons.checkroom),
                  _buildCategoryItem(context, 'Home', Icons.home_work),
                  _buildCategoryItem(context, 'Beauty', Icons.face),
                  _buildCategoryItem(context, 'Sports', Icons.sports_basketball),
                ],
              ),
            ),
            
            // Products grid
            Expanded(
              child: GridView.builder(
                padding: const EdgeInsets.all(8.0),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 0.7,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                ),
                itemCount: 10, // Replace with actual product count
                itemBuilder: (context, index) {
                  return Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Product Image
                        Expanded(
                          flex: 3,
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.grey[200],
                              borderRadius: BorderRadius.vertical(
                                top: Radius.circular(8),
                              ),
                            ),
                            child: Stack(
                              children: [
                                Center(
                                  child: Icon(Icons.image, size: 50),
                                ),
                                Positioned(
                                  top: 8,
                                  right: 8,
                                  child: IconButton(
                                    icon: Icon(Icons.favorite_border),
                                    onPressed: () {
                                      // TODO: Implement wishlist
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        // Product Details
                        Expanded(
                          flex: 2,
                          child: Padding(
                            padding: const EdgeInsets.all(8.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Product ${index + 1}',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                Text(
                                  '\$${(index + 1) * 10}.99',
                                  style: TextStyle(
                                    color: Theme.of(context).primaryColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                  ),
                                ),
                                ElevatedButton.icon(
                                  onPressed: () {
                                    cartProvider.addToCart(
                                      authProvider.currentUser!['Buyer_ID'].toString(),
                                      index + 1,
                                      1,
                                    );
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(
                                        content: Text('Added to cart'),
                                        duration: Duration(seconds: 1),
                                        action: SnackBarAction(
                                          label: 'View Cart',
                                          onPressed: () {
                                            // Navigate to cart
                                          },
                                        ),
                                      ),
                                    );
                                  },
                                  icon: Icon(Icons.shopping_cart_outlined),
                                  label: Text('Add'),
                                  style: ElevatedButton.styleFrom(
                                    minimumSize: Size(double.infinity, 36),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildCategoryItem(BuildContext context, String title, IconData icon) {
    return Container(
      width: 80,
      margin: EdgeInsets.symmetric(horizontal: 4),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: Theme.of(context).primaryColor,
            ),
          ),
          SizedBox(height: 4),
          Text(
            title,
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
} 