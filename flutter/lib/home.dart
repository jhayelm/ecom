import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar
          SliverAppBar(
            floating: true,
            backgroundColor: Colors.black.withOpacity(0.9),
            title: Row(
              children: [
                Text(
                  'Fenamaz',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            actions: [
              IconButton(
                icon: Icon(Icons.search, color: Colors.white),
                onPressed: () {},
              ),
              IconButton(
                icon: Icon(Icons.favorite_border, color: Colors.white),
                onPressed: () {},
              ),
              IconButton(
                icon: Icon(Icons.shopping_cart_outlined, color: Colors.white),
                onPressed: () {},
              ),
              IconButton(
                icon: Icon(Icons.person_outline, color: Colors.white),
                onPressed: () {},
              ),
            ],
          ),
          // Categories
          SliverToBoxAdapter(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.symmetric(vertical: 10),
              child: Row(
                children: [
                  _buildCategoryChip('Mobile Phone'),
                  _buildCategoryChip('Laptop'),
                  _buildCategoryChip('Desktop'),
                  _buildCategoryChip('Audio Equipment'),
                  _buildCategoryChip('Video Equipment'),
                  _buildCategoryChip('Smart Home Devices'),
                  _buildCategoryChip('Photography'),
                  _buildCategoryChip('Wearable Technology'),
                  _buildCategoryChip('Digital Accessories'),
                  _buildCategoryChip('Others'),
                ],
              ),
            ),
          ),
          // Hero Section
          SliverToBoxAdapter(
            child: Container(
              height: 500,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF1a1a2e),
                    Color(0xFF16213e),
                  ],
                ),
              ),
              child: Stack(
                children: [
                  // Neon Lines Effect
                  Positioned.fill(
                    child: CustomPaint(
                      painter: NeonLinesPainter(),
                    ),
                  ),
                  // Content
                  Padding(
                    padding: EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'DON\'T SETTLE FOR "ALMOST"\nWHEN YOU CAN HAVE\nTHE PERFECT PC!',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            height: 1.2,
                          ),
                        ),
                        SizedBox(height: 20),
                        Text(
                          'START BUILDING YOUR\nDREAM PC TODAY!',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        SizedBox(height: 30),
                        ElevatedButton(
                          onPressed: () {},
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                            padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                          ),
                          child: Text(
                            'Build Now',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChip(String label) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 4),
      child: Chip(
        label: Text(
          label,
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.blue.withOpacity(0.3),
      ),
    );
  }
}

// Custom painter for neon lines effect
class NeonLinesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.3)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    for (var i = 0; i < 10; i++) {
      canvas.drawLine(
        Offset(0, size.height * i / 10),
        Offset(size.width, size.height * (i + 1) / 10),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
} 