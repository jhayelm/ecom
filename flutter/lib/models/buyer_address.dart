class BuyerAddress {
  final int? addressId;
  final String houseNo;
  final String barangay;
  final String city;
  final String province;
  final String postalCode;
  final String country;

  BuyerAddress({
    this.addressId,
    required this.houseNo,
    required this.barangay,
    required this.city,
    required this.province,
    required this.postalCode,
    this.country = 'Philippines',
  });

  factory BuyerAddress.fromJson(Map<String, dynamic> json) {
    return BuyerAddress(
      addressId: json['Address_ID'],
      houseNo: json['House_No'],
      barangay: json['Barangay'],
      city: json['City'],
      province: json['Province'],
      postalCode: json['Postal_Code'],
      country: json['Country'] ?? 'Philippines',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Address_ID': addressId,
      'House_No': houseNo,
      'Barangay': barangay,
      'City': city,
      'Province': province,
      'Postal_Code': postalCode,
      'Country': country,
    };
  }
} 