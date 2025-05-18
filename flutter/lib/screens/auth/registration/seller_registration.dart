import 'package:flutter/material.dart';
import 'base_registration.dart';

class SellerRegistrationScreen extends BaseRegistrationScreen {
  const SellerRegistrationScreen({super.key});

  @override
  State<SellerRegistrationScreen> createState() => _SellerRegistrationScreenState();
}

class _SellerRegistrationScreenState extends BaseRegistrationState<SellerRegistrationScreen> {
  final _validIdTypeController = TextEditingController();
  final _validIdNumberController = TextEditingController();
  String? _validIdImagePath;
  
  final _businessPermitNumberController = TextEditingController();
  String? _businessPermitImagePath;

  Widget buildValidIdStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Step 3: Valid Information'),
        const SizedBox(height: 16),
        TextField(
          controller: _validIdTypeController,
          decoration: InputDecoration(
            labelText: 'Type of Valid ID*',
            hintText: 'SSS ID',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _validIdNumberController,
          decoration: InputDecoration(
            labelText: 'Valid ID Number*',
            hintText: 'Enter your valid ID number',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Upload Valid ID Picture*'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      // Handle file selection
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                    ),
                    child: const Text('Choose File'),
                  ),
                  const SizedBox(width: 16),
                  Text(_validIdImagePath ?? 'No file chosen'),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget buildBusinessInfoStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Step 4: Business Information'),
        const SizedBox(height: 16),
        TextField(
          controller: _businessPermitNumberController,
          decoration: InputDecoration(
            labelText: 'Business Permit Number*',
            hintText: 'Enter your business permit number',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Upload Business Permit*'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      // Handle file selection
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                    ),
                    child: const Text('Choose File'),
                  ),
                  const SizedBox(width: 16),
                  Text(_businessPermitImagePath ?? 'No file chosen'),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final steps = [
      buildPersonalInfoStep(),
      buildAddressStep(),
      buildValidIdStep(),
      buildBusinessInfoStep(),
      buildAccountStep(),
    ];

    return Scaffold(
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(24),
          child: Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(15),
            ),
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Register!',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.arrow_back),
                        onPressed: () {
                          Navigator.of(context).pop();
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Expanded(
                    child: SingleChildScrollView(
                      child: steps[currentStep],
                    ),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (currentStep > 0)
                        TextButton(
                          onPressed: () {
                            setState(() {
                              currentStep--;
                            });
                          },
                          child: const Text('Previous'),
                        ),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: () {
                          if (currentStep < steps.length - 1) {
                            setState(() {
                              currentStep++;
                            });
                          } else {
                            // Handle registration submission
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 12,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: Text(
                          currentStep < steps.length - 1 ? 'Next' : 'Submit',
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
} 