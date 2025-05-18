import 'package:flutter/material.dart';

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  bool _showArchived = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check_circle_outline),
            onPressed: () {
              // Handle mark all as read
            },
            tooltip: 'Mark All as Read',
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      hintText: 'Sort By',
                    ),
                    items: const [
                      DropdownMenuItem(value: 'newest', child: Text('Newest First')),
                      DropdownMenuItem(value: 'oldest', child: Text('Oldest First')),
                    ],
                    onChanged: (value) {
                      // Handle sort
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      hintText: 'Filter by Type',
                    ),
                    items: const [
                      DropdownMenuItem(value: 'all', child: Text('All')),
                      DropdownMenuItem(value: 'orders', child: Text('Orders')),
                      DropdownMenuItem(value: 'promotions', child: Text('Promotions')),
                      DropdownMenuItem(value: 'system', child: Text('System')),
                    ],
                    onChanged: (value) {
                      // Handle filter
                    },
                  ),
                ),
              ],
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Padding(
                padding: const EdgeInsets.only(right: 16),
                child: TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _showArchived = !_showArchived;
                    });
                  },
                  icon: Icon(_showArchived ? Icons.visibility_off : Icons.visibility),
                  label: Text(_showArchived ? 'Hide Archived' : 'Show Archived'),
                ),
              ),
            ],
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildNotificationCard(
                  title: 'Order #12345 has been shipped',
                  message: 'Your order is on its way! Expected delivery: 3-5 business days',
                  time: '2 hours ago',
                  type: NotificationType.order,
                ),
                _buildNotificationCard(
                  title: 'Special Offer!',
                  message: 'Get 20% off on all laptops this weekend',
                  time: '5 hours ago',
                  type: NotificationType.promotion,
                ),
                _buildNotificationCard(
                  title: 'System Maintenance',
                  message: 'The app will be under maintenance on Sunday, 2 AM - 4 AM',
                  time: '1 day ago',
                  type: NotificationType.system,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationCard({
    required String title,
    required String message,
    required String time,
    required NotificationType type,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: type.color.withOpacity(0.1),
          child: Icon(type.icon, color: type.color),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(message),
            const SizedBox(height: 4),
            Text(
              time,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'mark_read',
              child: Text('Mark as Read'),
            ),
            const PopupMenuItem(
              value: 'archive',
              child: Text('Archive'),
            ),
          ],
          onSelected: (value) {
            // Handle menu selection
          },
        ),
      ),
    );
  }
}

enum NotificationType {
  order(Icons.local_shipping, Colors.blue),
  promotion(Icons.local_offer, Colors.green),
  system(Icons.info, Colors.orange);

  final IconData icon;
  final Color color;

  const NotificationType(this.icon, this.color);
} 