class SellerAccount {
  final int? sellerId;
  final int? personalId;
  final int? addressId;
  final int? validId;
  final int? businessId;
  final String? phone;
  final String? email;
  final String password;
  final String status;
  final String role;
  final DateTime timestamp;

  SellerAccount({
    this.sellerId,
    this.personalId,
    this.addressId,
    this.validId,
    this.businessId,
    this.phone,
    this.email,
    required this.password,
    required this.status,
    required this.role,
    required this.timestamp,
  });

  factory SellerAccount.fromJson(Map<String, dynamic> json) {
    return SellerAccount(
      sellerId: json['Seller_ID'],
      personalId: json['Personal_ID'],
      addressId: json['Address_ID'],
      validId: json['Valid_ID'],
      businessId: json['Business_ID'],
      phone: json['Phone'],
      email: json['Email'],
      password: json['Password'],
      status: json['Status'],
      role: json['Role'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Seller_ID': sellerId,
      'Personal_ID': personalId,
      'Address_ID': addressId,
      'Valid_ID': validId,
      'Business_ID': businessId,
      'Phone': phone,
      'Email': email,
      'Password': password,
      'Status': status,
      'Role': role,
      'timestamp': timestamp.toIso8601String(),
    };
  }
} 