import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        const CircleAvatar(
          radius: 50,
          backgroundColor: Colors.blue,
          child: Icon(Icons.person, size: 50, color: Colors.white),
        ),
        const SizedBox(height: 16),
        const Text(
          'John Doe', // Replace with actual user name
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 32),
        const ListTile(
          leading: Icon(Icons.email),
          title: Text('Email'),
          subtitle: Text('john.doe@example.com'), // Replace with actual email
        ),
        const ListTile(
          leading: Icon(Icons.phone),
          title: Text('Phone'),
          subtitle: Text('+1 234 567 8900'), // Replace with actual phone
        ),
        const ListTile(
          leading: Icon(Icons.location_on),
          title: Text('Address'),
          subtitle: Text('123 Main St, City, Country'), // Replace with actual address
        ),
        const Divider(),
        ListTile(
          leading: const Icon(Icons.shopping_bag),
          title: const Text('My Orders'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            // TODO: Navigate to orders screen
          },
        ),
        ListTile(
          leading: const Icon(Icons.favorite),
          title: const Text('Wishlist'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            // TODO: Navigate to wishlist screen
          },
        ),
        ListTile(
          leading: const Icon(Icons.settings),
          title: const Text('Settings'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            // TODO: Navigate to settings screen
          },
        ),
        const Divider(),
        ListTile(
          leading: const Icon(Icons.logout, color: Colors.red),
          title: const Text(
            'Logout',
            style: TextStyle(color: Colors.red),
          ),
          onTap: () async {
            await Provider.of<AuthProvider>(context, listen: false).logout();
            if (context.mounted) {
              Navigator.pushReplacementNamed(context, '/login');
            }
          },
        ),
      ],
    );
  }
} 