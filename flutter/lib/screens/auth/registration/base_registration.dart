import 'package:flutter/material.dart';

abstract class BaseRegistrationScreen extends StatefulWidget {
  const BaseRegistrationScreen({super.key});
}

class BaseRegistrationState<T extends BaseRegistrationScreen> extends State<T> {
  int currentStep = 0;
  final _formKey = GlobalKey<FormState>();
  
  // Common controllers
  final _firstNameController = TextEditingController();
  final _middleNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _suffixController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _sexController = TextEditingController();
  
  // Address controllers
  final _provinceController = TextEditingController();
  final _cityController = TextEditingController();
  final _barangayController = TextEditingController();
  final _houseNumberController = TextEditingController();
  final _zipCodeController = TextEditingController();
  
  // Account controllers
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  Widget buildPersonalInfoStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Step 1: Personal Information'),
        const SizedBox(height: 16),
        TextField(
          controller: _firstNameController,
          decoration: InputDecoration(
            labelText: 'First Name*',
            hintText: 'Enter your first name',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _middleNameController,
          decoration: InputDecoration(
            labelText: 'Middle Name*',
            hintText: 'Enter your middle name',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              flex: 2,
              child: TextField(
                controller: _lastNameController,
                decoration: InputDecoration(
                  labelText: 'Last Name*',
                  hintText: 'Enter your last name',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: TextField(
                controller: _suffixController,
                decoration: InputDecoration(
                  labelText: 'Suffix',
                  hintText: 'None',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _sexController,
                decoration: InputDecoration(
                  labelText: 'Sex*',
                  hintText: 'Select',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: TextField(
                controller: _birthDateController,
                decoration: InputDecoration(
                  labelText: 'Birthdate*',
                  hintText: 'dd/mm/yyyy',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  suffixIcon: const Icon(Icons.calendar_today),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget buildAddressStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Step 2: Address Information'),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _provinceController,
                decoration: InputDecoration(
                  labelText: 'Province*',
                  hintText: 'Select your province',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: TextField(
                controller: _zipCodeController,
                decoration: InputDecoration(
                  labelText: 'Zip Code*',
                  hintText: 'ex. 4027',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _cityController,
          decoration: InputDecoration(
            labelText: 'City*',
            hintText: 'Select your city',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _barangayController,
          decoration: InputDecoration(
            labelText: 'Barangay*',
            hintText: 'Select your barangay',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _houseNumberController,
          decoration: InputDecoration(
            labelText: 'House No.*',
            hintText: 'Enter your house number',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ],
    );
  }

  Widget buildAccountStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Step 4: Account Information'),
        const SizedBox(height: 16),
        TextField(
          controller: _phoneController,
          decoration: InputDecoration(
            labelText: 'Phone No.',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _emailController,
          decoration: InputDecoration(
            labelText: 'Email',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'Password',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility : Icons.visibility_off,
              ),
              onPressed: () {
                setState(() {
                  _obscurePassword = !_obscurePassword;
                });
              },
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _confirmPasswordController,
          obscureText: _obscureConfirmPassword,
          decoration: InputDecoration(
            labelText: 'Confirm Password',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmPassword ? Icons.visibility : Icons.visibility_off,
              ),
              onPressed: () {
                setState(() {
                  _obscureConfirmPassword = !_obscureConfirmPassword;
                });
              },
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Placeholder();
  }
} 