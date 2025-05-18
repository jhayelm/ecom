import 'package:flutter/material.dart';

class CategoryPage extends StatefulWidget {
  final String categoryName;

  const CategoryPage({super.key, required this.categoryName});

  @override
  State<CategoryPage> createState() => _CategoryPageState();
}

class _CategoryPageState extends State<CategoryPage> {
  String _sortBy = 'Most Recent';
  final _minPriceController = TextEditingController(text: '0');
  final _maxPriceController = TextEditingController(text: '0');
  bool _isTopSelling = false;
  bool _isPopular = false;
  bool _isTopViews = false;
  bool _isYouMayLike = false;
  bool _showFilter = false;

  @override
  Widget build(BuildContext context) {
    final isSmallScreen = MediaQuery.of(context).size.width < 600;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(widget.categoryName),
        actions: [
          if (isSmallScreen)
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: () {
                setState(() {
                  _showFilter = !_showFilter;
                });
              },
            ),
        ],
      ),
      body: isSmallScreen
          ? Column(
              children: [
                if (_showFilter) _buildFilterPanel(),
                Expanded(
                  child: _buildProductGrid(crossAxisCount: 2),
                ),
              ],
            )
          : Row(
              children: [
                SizedBox(
                  width: MediaQuery.of(context).size.width * 0.3,
                  child: _buildFilterPanel(),
                ),
                Expanded(
                  child: _buildProductGrid(crossAxisCount: 3),
                ),
              ],
            ),
    );
  }

  Widget _buildFilterPanel() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        border: Border(
          bottom: BorderSide(color: Colors.grey[200]!),
        ),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Filter',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            const Text('Min Price (PHP)'),
            const SizedBox(height: 8),
            TextField(
              controller: _minPriceController,
              decoration: InputDecoration(
                prefixText: '₱ ',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            const Text('Max Price (PHP)'),
            const SizedBox(height: 8),
            TextField(
              controller: _maxPriceController,
              decoration: InputDecoration(
                prefixText: '₱ ',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            const Text('Sort by:'),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _sortBy,
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'Most Recent',
                  child: Text('Most Recent'),
                ),
                DropdownMenuItem(
                  value: 'Price: Low to High',
                  child: Text('Price: Low to High'),
                ),
                DropdownMenuItem(
                  value: 'Price: High to Low',
                  child: Text('Price: High to Low'),
                ),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _sortBy = value;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            const Text('Other'),
            CheckboxListTile(
              title: const Text('Top Selling'),
              value: _isTopSelling,
              onChanged: (value) {
                setState(() {
                  _isTopSelling = value ?? false;
                });
              },
              dense: true,
              contentPadding: EdgeInsets.zero,
            ),
            CheckboxListTile(
              title: const Text('Popular'),
              value: _isPopular,
              onChanged: (value) {
                setState(() {
                  _isPopular = value ?? false;
                });
              },
              dense: true,
              contentPadding: EdgeInsets.zero,
            ),
            CheckboxListTile(
              title: const Text('Top Views'),
              value: _isTopViews,
              onChanged: (value) {
                setState(() {
                  _isTopViews = value ?? false;
                });
              },
              dense: true,
              contentPadding: EdgeInsets.zero,
            ),
            CheckboxListTile(
              title: const Text('You May Like'),
              value: _isYouMayLike,
              onChanged: (value) {
                setState(() {
                  _isYouMayLike = value ?? false;
                });
              },
              dense: true,
              contentPadding: EdgeInsets.zero,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      setState(() {
                        _minPriceController.text = '0';
                        _maxPriceController.text = '0';
                        _sortBy = 'Most Recent';
                        _isTopSelling = false;
                        _isPopular = false;
                        _isTopViews = false;
                        _isYouMayLike = false;
                      });
                    },
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Reset'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      if (MediaQuery.of(context).size.width < 600) {
                        setState(() {
                          _showFilter = false;
                        });
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Apply'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductGrid({required int crossAxisCount}) {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.75,
      ),
      itemCount: 12,
      itemBuilder: (context, index) {
        return Card(
          elevation: 2,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.grey[800],
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(4),
                    ),
                  ),
                  child: Stack(
                    children: [
                      Center(
                        child: Icon(
                          Icons.phone_android,
                          size: 50,
                          color: Colors.grey[600],
                        ),
                      ),
                      Positioned(
                        top: 8,
                        right: 8,
                        child: IconButton(
                          icon: const Icon(
                            Icons.favorite_border,
                            color: Colors.white,
                          ),
                          onPressed: () {},
                          iconSize: 20,
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Phone Model ${index + 1}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₱${((index + 1) * 10000).toString()}',
                      style: const TextStyle(
                        color: Colors.blue,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.shopping_cart, size: 16),
                        label: const Text('Add'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
} 