import 'package:flutter/material.dart';

class CategoryScreen extends StatefulWidget {
  const CategoryScreen({super.key});

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();
  RangeValues _priceRange = const RangeValues(10000, 120000);
  String _sortBy = 'popular';
  final List<String> _selectedFilters = [];
  bool _showCart = false;
  bool _showSearchBar = true;
  String? _selectedCategory;

  final List<Map<String, String>> _categories = [
    {
      'name': 'Mobile Phone',
      'image': 'assets/images/category_mobile.png',
    },
    {
      'name': 'Laptop',
      'image': 'assets/images/category_laptop.png',
    },
    {
      'name': 'Desktop',
      'image': 'assets/images/category_desktop.png',
    },
    {
      'name': 'Audio Equipment',
      'image': 'assets/images/category_audio.png',
    },
    {
      'name': 'Video Equipment',
      'image': 'assets/images/category_video.png',
    },
    {
      'name': 'Smart Home Devices',
      'image': 'assets/images/category_smart.png',
    },
    {
      'name': 'Photography',
      'image': 'assets/images/category_photo.png',
    },
    {
      'name': 'Wearable Technology',
      'image': 'assets/images/category_wearable.png',
    },
    {
      'name': 'Digital Accessories',
      'image': 'assets/images/category_accessories.png',
    },
    {
      'name': 'Others',
      'image': 'assets/images/category_others.png',
    },
  ];

  final List<Map<String, dynamic>> _products = [
    // Laptops
    {
      'id': 'l1',
      'name': 'Acer Nitro 5',
      'category': 'Laptop',
      'description': 'Gaming Laptop',
      'price': 54995.0,
      'rating': 4.5,
      'reviews': 128,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'l2',
      'name': 'ASUS ROG Strix G15',
      'category': 'Laptop',
      'description': 'Gaming Laptop',
      'price': 89995.0,
      'rating': 4.7,
      'reviews': 95,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'l3',
      'name': 'MacBook Pro M2',
      'category': 'Laptop',
      'description': 'Professional Laptop',
      'price': 129995.0,
      'rating': 4.8,
      'reviews': 156,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'l4',
      'name': 'Lenovo Legion 5',
      'category': 'Laptop',
      'description': 'Gaming Laptop',
      'price': 69995.0,
      'rating': 4.4,
      'reviews': 112,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'l5',
      'name': 'Dell XPS 15',
      'category': 'Laptop',
      'description': 'Professional Laptop',
      'price': 94995.0,
      'rating': 4.6,
      'reviews': 89,
      'image': 'assets/images/product1.png',
    },
    
    // Mobile Phones
    {
      'id': 'm1',
      'name': 'iPhone 15 Pro Max',
      'category': 'Mobile Phone',
      'description': 'Flagship Smartphone',
      'price': 89995.0,
      'rating': 4.8,
      'reviews': 245,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'm2',
      'name': 'Samsung Galaxy S24 Ultra',
      'category': 'Mobile Phone',
      'description': 'Android Flagship',
      'price': 79995.0,
      'rating': 4.7,
      'reviews': 189,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'm3',
      'name': 'Google Pixel 8 Pro',
      'category': 'Mobile Phone',
      'description': 'Premium Android',
      'price': 69995.0,
      'rating': 4.6,
      'reviews': 156,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'm4',
      'name': 'OnePlus 12',
      'category': 'Mobile Phone',
      'description': 'Flagship Killer',
      'price': 59995.0,
      'rating': 4.5,
      'reviews': 134,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'm5',
      'name': 'Xiaomi 14 Pro',
      'category': 'Mobile Phone',
      'description': 'Premium Smartphone',
      'price': 49995.0,
      'rating': 4.4,
      'reviews': 112,
      'image': 'assets/images/product2.png',
    },

    // Desktops
    {
      'id': 'd1',
      'name': 'ROG Strix GT35',
      'category': 'Desktop',
      'description': 'Gaming Desktop',
      'price': 159995.0,
      'rating': 4.8,
      'reviews': 78,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'd2',
      'name': 'iMac M3',
      'category': 'Desktop',
      'description': 'All-in-One Desktop',
      'price': 129995.0,
      'rating': 4.7,
      'reviews': 92,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'd3',
      'name': 'Alienware Aurora R15',
      'category': 'Desktop',
      'description': 'Gaming Desktop',
      'price': 189995.0,
      'rating': 4.9,
      'reviews': 65,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'd4',
      'name': 'HP Omen 45L',
      'category': 'Desktop',
      'description': 'Gaming Desktop',
      'price': 149995.0,
      'rating': 4.6,
      'reviews': 83,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'd5',
      'name': 'MSI MEG Aegis Ti5',
      'category': 'Desktop',
      'description': 'Gaming Desktop',
      'price': 199995.0,
      'rating': 4.8,
      'reviews': 71,
      'image': 'assets/images/product3.png',
    },
    // Additional Desktop Products
    {
      'id': 'd6',
      'name': 'LG UltraGear 32GQ950',
      'category': 'Desktop',
      'description': '4K 144Hz Gaming Monitor',
      'price': 54995.0,
      'rating': 4.7,
      'reviews': 145,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'd7',
      'name': 'Samsung Odyssey G9',
      'category': 'Desktop',
      'description': '49" Ultra-wide Gaming Monitor',
      'price': 89995.0,
      'rating': 4.8,
      'reviews': 112,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'd8',
      'name': 'ASUS ProArt PA32UCG',
      'category': 'Desktop',
      'description': 'Professional 4K Monitor',
      'price': 129995.0,
      'rating': 4.9,
      'reviews': 78,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'd9',
      'name': 'Corsair iCUE 5000X',
      'category': 'Desktop',
      'description': 'RGB Gaming Case',
      'price': 12995.0,
      'rating': 4.6,
      'reviews': 234,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'd10',
      'name': 'Lian Li O11 Dynamic EVO',
      'category': 'Desktop',
      'description': 'Premium PC Case',
      'price': 14995.0,
      'rating': 4.7,
      'reviews': 189,
      'image': 'assets/images/product4.png',
    },

    // Audio Equipment
    {
      'id': 'a1',
      'name': 'Sony WH-1000XM5',
      'category': 'Audio Equipment',
      'description': 'Wireless Headphones',
      'price': 19995.0,
      'rating': 4.8,
      'reviews': 312,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'a2',
      'name': 'Apple AirPods Pro 2',
      'category': 'Audio Equipment',
      'description': 'TWS Earbuds',
      'price': 14995.0,
      'rating': 4.7,
      'reviews': 428,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'a3',
      'name': 'Bose 700',
      'category': 'Audio Equipment',
      'description': 'Noise Cancelling Headphones',
      'price': 24995.0,
      'rating': 4.6,
      'reviews': 245,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'a4',
      'name': 'JBL Quantum 800',
      'category': 'Audio Equipment',
      'description': 'Gaming Headset',
      'price': 12995.0,
      'rating': 4.5,
      'reviews': 167,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'a5',
      'name': 'Sennheiser HD 660S',
      'category': 'Audio Equipment',
      'description': 'Professional Headphones',
      'price': 29995.0,
      'rating': 4.9,
      'reviews': 134,
      'image': 'assets/images/product4.png',
    },

    // Video Equipment
    {
      'id': 'v1',
      'name': 'Sony A7 IV',
      'category': 'Video Equipment',
      'description': 'Mirrorless Camera',
      'price': 129995.0,
      'rating': 4.8,
      'reviews': 89,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'v2',
      'name': 'Canon EOS R6',
      'category': 'Video Equipment',
      'description': 'Mirrorless Camera',
      'price': 149995.0,
      'rating': 4.7,
      'reviews': 76,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'v3',
      'name': 'DJI RS 3 Pro',
      'category': 'Video Equipment',
      'description': 'Camera Gimbal',
      'price': 34995.0,
      'rating': 4.6,
      'reviews': 112,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'v4',
      'name': 'Blackmagic Pocket 6K',
      'category': 'Video Equipment',
      'description': 'Cinema Camera',
      'price': 199995.0,
      'rating': 4.9,
      'reviews': 45,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'v5',
      'name': 'Atomos Ninja V',
      'category': 'Video Equipment',
      'description': 'External Monitor Recorder',
      'price': 44995.0,
      'rating': 4.7,
      'reviews': 67,
      'image': 'assets/images/product1.png',
    },

    // Smart Home Devices
    {
      'id': 'sh1',
      'name': 'Google Nest Hub Max',
      'category': 'Smart Home Devices',
      'description': 'Smart Display with Assistant',
      'price': 12995.0,
      'rating': 4.6,
      'reviews': 156,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'sh2',
      'name': 'Amazon Echo Show 10',
      'category': 'Smart Home Devices',
      'description': 'Smart Display with Alexa',
      'price': 14995.0,
      'rating': 4.5,
      'reviews': 142,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'sh3',
      'name': 'Philips Hue Starter Kit',
      'category': 'Smart Home Devices',
      'description': 'Smart Lighting System',
      'price': 9995.0,
      'rating': 4.7,
      'reviews': 234,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'sh4',
      'name': 'Ring Video Doorbell Pro',
      'category': 'Smart Home Devices',
      'description': 'Smart Doorbell with Camera',
      'price': 11995.0,
      'rating': 4.4,
      'reviews': 189,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'sh5',
      'name': 'Aqara Smart Hub M2',
      'category': 'Smart Home Devices',
      'description': 'Smart Home Control Center',
      'price': 7995.0,
      'rating': 4.3,
      'reviews': 98,
      'image': 'assets/images/product2.png',
    },

    // Photography Equipment
    {
      'id': 'p1',
      'name': 'Canon EOS R5',
      'category': 'Photography',
      'description': 'Professional Mirrorless Camera',
      'price': 189995.0,
      'rating': 4.9,
      'reviews': 145,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'p2',
      'name': 'Sony A7R V',
      'category': 'Photography',
      'description': 'High-Resolution Mirrorless',
      'price': 199995.0,
      'rating': 4.8,
      'reviews': 112,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'p3',
      'name': 'Nikon Z9',
      'category': 'Photography',
      'description': 'Flagship Mirrorless Camera',
      'price': 249995.0,
      'rating': 4.9,
      'reviews': 89,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'p4',
      'name': 'Profoto B10X Plus',
      'category': 'Photography',
      'description': 'Professional Studio Light',
      'price': 149995.0,
      'rating': 4.7,
      'reviews': 67,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'p5',
      'name': 'DJI RS 3 Pro Combo',
      'category': 'Photography',
      'description': 'Professional Camera Stabilizer',
      'price': 49995.0,
      'rating': 4.6,
      'reviews': 156,
      'image': 'assets/images/product3.png',
    },

    // Wearable Technology
    {
      'id': 'w1',
      'name': 'Apple Watch Ultra 2',
      'category': 'Wearable Technology',
      'description': 'Premium Smartwatch',
      'price': 54995.0,
      'rating': 4.8,
      'reviews': 234,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'w2',
      'name': 'Samsung Galaxy Watch 6 Pro',
      'category': 'Wearable Technology',
      'description': 'Advanced Smartwatch',
      'price': 24995.0,
      'rating': 4.6,
      'reviews': 189,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'w3',
      'name': 'Garmin Fenix 7X',
      'category': 'Wearable Technology',
      'description': 'Multisport GPS Watch',
      'price': 44995.0,
      'rating': 4.7,
      'reviews': 156,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'w4',
      'name': 'Oura Ring Gen 3',
      'category': 'Wearable Technology',
      'description': 'Smart Health Ring',
      'price': 19995.0,
      'rating': 4.5,
      'reviews': 123,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'w5',
      'name': 'Whoop 4.0',
      'category': 'Wearable Technology',
      'description': 'Fitness Performance Band',
      'price': 14995.0,
      'rating': 4.4,
      'reviews': 98,
      'image': 'assets/images/product4.png',
    },

    // Digital Accessories
    {
      'id': 'da1',
      'name': 'Samsung T7 Shield 2TB',
      'category': 'Digital Accessories',
      'description': 'Portable SSD',
      'price': 12995.0,
      'rating': 4.7,
      'reviews': 245,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'da2',
      'name': 'Anker 737 GaNPrime',
      'category': 'Digital Accessories',
      'description': '120W Charging Station',
      'price': 6995.0,
      'rating': 4.6,
      'reviews': 189,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'da3',
      'name': 'Logitech MX Master 3S',
      'category': 'Digital Accessories',
      'description': 'Premium Wireless Mouse',
      'price': 5995.0,
      'rating': 4.8,
      'reviews': 312,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'da4',
      'name': 'Keychron Q1 Pro',
      'category': 'Digital Accessories',
      'description': 'Mechanical Keyboard',
      'price': 8995.0,
      'rating': 4.7,
      'reviews': 167,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'da5',
      'name': 'CalDigit TS4',
      'category': 'Digital Accessories',
      'description': 'Thunderbolt 4 Dock',
      'price': 19995.0,
      'rating': 4.9,
      'reviews': 134,
      'image': 'assets/images/product1.png',
    },

    // Others (Computer Parts, Gaming Furniture & Accessories)
    {
      'id': 'o1',
      'name': 'NVIDIA RTX 4090',
      'category': 'Others',
      'description': 'Graphics Card',
      'price': 89995.0,
      'rating': 4.9,
      'reviews': 178,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'o2',
      'name': 'AMD Ryzen 9 7950X3D',
      'category': 'Others',
      'description': 'Desktop Processor',
      'price': 44995.0,
      'rating': 4.8,
      'reviews': 156,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'o3',
      'name': 'Samsung 990 Pro 4TB',
      'category': 'Others',
      'description': 'NVMe SSD',
      'price': 34995.0,
      'rating': 4.7,
      'reviews': 234,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'o4',
      'name': 'ASUS ROG Maximus Z790',
      'category': 'Others',
      'description': 'Gaming Motherboard',
      'price': 39995.0,
      'rating': 4.6,
      'reviews': 145,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'o5',
      'name': 'Corsair HX1500i',
      'category': 'Others',
      'description': 'Power Supply Unit',
      'price': 24995.0,
      'rating': 4.8,
      'reviews': 189,
      'image': 'assets/images/product2.png',
    },
    // Additional Others Products
    {
      'id': 'o6',
      'name': 'Secretlab TITAN Evo 2022',
      'category': 'Others',
      'description': 'Premium Gaming Chair',
      'price': 29995.0,
      'rating': 4.8,
      'reviews': 312,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'o7',
      'name': 'DXRacer Air Mesh',
      'category': 'Others',
      'description': 'Ergonomic Gaming Chair',
      'price': 24995.0,
      'rating': 4.6,
      'reviews': 245,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'o8',
      'name': 'FlexiSpot E7 Pro',
      'category': 'Others',
      'description': 'Electric Gaming Desk',
      'price': 34995.0,
      'rating': 4.7,
      'reviews': 178,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'o9',
      'name': 'Thermaltake Battlestation',
      'category': 'Others',
      'description': 'RGB Gaming Desk',
      'price': 39995.0,
      'rating': 4.5,
      'reviews': 156,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'o10',
      'name': 'NZXT H510 Flow',
      'category': 'Others',
      'description': 'Airflow PC Case',
      'price': 8995.0,
      'rating': 4.7,
      'reviews': 289,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'o11',
      'name': 'be quiet! Dark Rock Pro 4',
      'category': 'Others',
      'description': 'CPU Air Cooler',
      'price': 6995.0,
      'rating': 4.8,
      'reviews': 234,
      'image': 'assets/images/product4.png',
    },
    {
      'id': 'o12',
      'name': 'NZXT Kraken Z73',
      'category': 'Others',
      'description': '360mm AIO Liquid Cooler',
      'price': 14995.0,
      'rating': 4.9,
      'reviews': 198,
      'image': 'assets/images/product1.png',
    },
    {
      'id': 'o13',
      'name': 'G.SKILL Trident Z5 RGB',
      'category': 'Others',
      'description': '32GB DDR5-6400 RAM',
      'price': 12995.0,
      'rating': 4.7,
      'reviews': 167,
      'image': 'assets/images/product2.png',
    },
    {
      'id': 'o14',
      'name': 'CableMod Pro Kit',
      'category': 'Others',
      'description': 'Custom PSU Cables',
      'price': 4995.0,
      'rating': 4.6,
      'reviews': 145,
      'image': 'assets/images/product3.png',
    },
    {
      'id': 'o15',
      'name': 'Autonomous SmartDesk Core',
      'category': 'Others',
      'description': 'Height Adjustable Desk',
      'price': 29995.0,
      'rating': 4.5,
      'reviews': 223,
      'image': 'assets/images/product4.png',
    },
  ];

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.offset > 100 && _showSearchBar) {
      setState(() {
        _showSearchBar = false;
      });
    } else if (_scrollController.offset <= 100 && !_showSearchBar) {
      setState(() {
        _showSearchBar = true;
      });
    }
  }

  List<Map<String, dynamic>> get filteredProducts {
    return _products.where((product) {
      if (_selectedCategory != null && product['category'] != _selectedCategory) {
        return false;
      }
      final price = product['price'] as num;
      if (price < _priceRange.start || price > _priceRange.end) {
        return false;
      }
      if (_searchController.text.isNotEmpty) {
        final searchTerm = _searchController.text.toLowerCase();
        final name = product['name'].toString().toLowerCase();
        final description = product['description'].toString().toLowerCase();
        if (!name.contains(searchTerm) && !description.contains(searchTerm)) {
          return false;
        }
      }
      if (_selectedFilters.isNotEmpty) {
        // Implement filter logic here based on your needs
        // For example, "Top Selling" could be based on number of reviews
        if (_selectedFilters.contains('Top Selling') && product['reviews'] < 200) {
          return false;
        }
        // Add more filter logic as needed
      }
      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Categories'),
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_cart_outlined),
                onPressed: () {
                  setState(() {
                    _showCart = !_showCart;
                  });
                },
              ),
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 16,
                    minHeight: 16,
                  ),
                  child: const Text(
                    '3',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      body: Stack(
        children: [
          CustomScrollView(
            controller: _scrollController,
            slivers: [
              SliverToBoxAdapter(
                child: Column(
                  children: [
                    // Categories bar
                    Container(
                      height: 100,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: _categories.length,
                        itemBuilder: (context, index) {
                          final category = _categories[index];
                          final isSelected = _selectedCategory == category['name'];
                          return Padding(
                            padding: const EdgeInsets.only(right: 16),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                InkWell(
                                  onTap: () {
                                    setState(() {
                                      _selectedCategory = isSelected ? null : category['name'];
                                    });
                                  },
                                  child: Container(
                                    width: 60,
                                    height: 60,
                                    decoration: BoxDecoration(
                                      color: isSelected ? Colors.blue.withOpacity(0.1) : Colors.grey[100],
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(
                                        color: isSelected ? Colors.blue : Colors.transparent,
                                        width: 2,
                                      ),
                                    ),
                                    child: ClipRRect(
                                      borderRadius: BorderRadius.circular(10),
                                      child: Image.asset(
                                        category['image']!,
                                        fit: BoxFit.cover,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  category['name']!,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isSelected ? Colors.blue : Colors.black87,
                                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                    // Search and filters
                    if (_showSearchBar)
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 8),
                            SearchBar(
                              controller: _searchController,
                              hintText: 'Search in category...',
                              leading: const Icon(Icons.search),
                              trailing: [
                                if (_searchController.text.isNotEmpty)
                                  IconButton(
                                    icon: const Icon(Icons.clear),
                                    onPressed: () {
                                      _searchController.clear();
                                      setState(() {});
                                    },
                                  ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'Price Range',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            RangeSlider(
                              values: _priceRange,
                              min: 10000,
                              max: 120000,
                              divisions: 22,
                              labels: RangeLabels(
                                '₱${_priceRange.start.round()}',
                                '₱${_priceRange.end.round()}',
                              ),
                              onChanged: (values) {
                                setState(() {
                                  _priceRange = values;
                                });
                              },
                            ),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '₱${_priceRange.start.round()}',
                                  style: const TextStyle(color: Colors.grey),
                                ),
                                Text(
                                  '₱${_priceRange.end.round()}',
                                  style: const TextStyle(color: Colors.grey),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            SingleChildScrollView(
                              scrollDirection: Axis.horizontal,
                              child: Row(
                                children: [
                                  _buildFilterChip('Top Selling'),
                                  const SizedBox(width: 8),
                                  _buildFilterChip('New Arrival'),
                                  const SizedBox(width: 8),
                                  _buildFilterChip('On Sale'),
                                  const SizedBox(width: 8),
                                  _buildFilterChip('Popular'),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              // Product grid
              SliverPadding(
                padding: const EdgeInsets.all(16),
                sliver: SliverGrid(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 0.65,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                  ),
                  delegate: SliverChildBuilderDelegate(
                    (context, index) => _buildProductCard(filteredProducts[index]),
                    childCount: filteredProducts.length,
                  ),
                ),
              ),
            ],
          ),
          if (_showCart)
            Positioned(
              top: 0,
              right: 0,
              bottom: 0,
              child: _buildCartPanel(),
            ),
        ],
      ),
    );
  }

  Widget _buildCartPanel() {
    return Container(
      width: MediaQuery.of(context).size.width * 0.85,
      color: Theme.of(context).scaffoldBackgroundColor,
      child: Column(
        children: [
          AppBar(
            title: const Text('Shopping Cart'),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                setState(() {
                  _showCart = false;
                });
              },
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: 3, // TODO: Replace with actual cart items
              itemBuilder: (context, index) {
                return _buildCartItem();
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                ),
              ],
            ),
            child: SafeArea(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Total:',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text(
                        '₱164,985',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      // TODO: Navigate to checkout
                    },
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(48),
                    ),
                    child: const Text('Proceed to Checkout'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCartItem() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
                image: const DecorationImage(
                  image: AssetImage('assets/images/product1.png'),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Acer Nitro 5',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '₱54,995',
                    style: TextStyle(
                      color: Colors.blue,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove, size: 20),
                        onPressed: () {
                          // TODO: Decrease quantity
                        },
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                      const SizedBox(width: 12),
                      const Text('1'), // TODO: Show actual quantity
                      const SizedBox(width: 12),
                      IconButton(
                        icon: const Icon(Icons.add, size: 20),
                        onPressed: () {
                          // TODO: Increase quantity
                        },
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.delete_outline, size: 20),
                        onPressed: () {
                          // TODO: Remove from cart
                        },
                        color: Colors.red,
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label) {
    final isSelected = _selectedFilters.contains(label);
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          if (selected) {
            _selectedFilters.add(label);
          } else {
            _selectedFilters.remove(label);
          }
        });
      },
    );
  }

  Widget _buildProductCard(Map<String, dynamic> product) {
    final price = product['price'] as double;
    final rating = product['rating'] as double;
    final reviews = product['reviews'] as int;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AspectRatio(
            aspectRatio: 1,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.grey[200],
                image: DecorationImage(
                  image: AssetImage(product['image'] as String),
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product['name'] as String,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    product['description'] as String,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₱${price.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  const Spacer(),
                  Row(
                    children: [
                      const Icon(
                        Icons.star,
                        size: 14,
                        color: Colors.amber,
                      ),
                      Text(
                        rating.toString(),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        ' ($reviews)',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.add_shopping_cart, size: 20),
                        onPressed: () {
                          // TODO: Add to cart using CartService
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Added ${product['name']} to cart'),
                              duration: const Duration(seconds: 1),
                            ),
                          );
                        },
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
} 