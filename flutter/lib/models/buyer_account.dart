class BuyerAccount {
  final int? buyerId;
  final int? personalId;
  final int? addressId;
  final int? validId;
  final String phone;
  final String email;
  final String password;
  final String? profilePic;
  final String status;
  final String role;
  final DateTime timestamp;

  BuyerAccount({
    this.buyerId,
    this.personalId,
    this.addressId,
    this.validId,
    required this.phone,
    required this.email,
    required this.password,
    this.profilePic,
    required this.status,
    required this.role,
    required this.timestamp,
  });

  factory BuyerAccount.fromJson(Map<String, dynamic> json) {
    return BuyerAccount(
      buyerId: json['Buyer_ID'],
      personalId: json['Personal_ID'],
      addressId: json['Address_ID'],
      validId: json['Valid_ID'],
      phone: json['Phone'],
      email: json['Email'],
      password: json['Password'],
      profilePic: json['Profile_Pic'],
      status: json['Status'],
      role: json['Role'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Buyer_ID': buyerId,
      'Personal_ID': personalId,
      'Address_ID': addressId,
      'Valid_ID': validId,
      'Phone': phone,
      'Email': email,
      'Password': password,
      'Profile_Pic': profilePic,
      'Status': status,
      'Role': role,
      'timestamp': timestamp.toIso8601String(),
    };
  }
} 