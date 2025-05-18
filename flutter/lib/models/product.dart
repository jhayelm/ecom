class Product {
  final int? productId;
  final int? sellerId;
  final int? productInfoId;
  final String productCategory;
  final int? totalStocks;
  final String status;
  final DateTime timeAdded;

  Product({
    this.productId,
    this.sellerId,
    this.productInfoId,
    required this.productCategory,
    this.totalStocks,
    required this.status,
    required this.timeAdded,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      productId: json['Product_ID'],
      sellerId: json['Seller_ID'],
      productInfoId: json['Product_Info_ID'],
      productCategory: json['Product_Category'],
      totalStocks: json['Total_Stocks'],
      status: json['Status'],
      timeAdded: DateTime.parse(json['time_added']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Product_ID': productId,
      'Seller_ID': sellerId,
      'Product_Info_ID': productInfoId,
      'Product_Category': productCategory,
      'Total_Stocks': totalStocks,
      'Status': status,
      'time_added': timeAdded.toIso8601String(),
    };
  }
} 