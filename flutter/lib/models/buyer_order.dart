class BuyerOrder {
  final int? orderId;
  final int? productId;
  final int? sellerId;
  final int? shopId;
  final int? buyerId;
  final int quantity;
  final double totalAmount;
  final String paymentMethod;
  final String paymentStatus;
  final String status;
  final DateTime dateOrdered;

  BuyerOrder({
    this.orderId,
    this.productId,
    this.sellerId,
    this.shopId,
    this.buyerId,
    required this.quantity,
    required this.totalAmount,
    required this.paymentMethod,
    required this.paymentStatus,
    required this.status,
    required this.dateOrdered,
  });

  factory BuyerOrder.fromJson(Map<String, dynamic> json) {
    return BuyerOrder(
      orderId: json['Order_ID'],
      productId: json['Product_ID'],
      sellerId: json['Seller_ID'],
      shopId: json['Shop_ID'],
      buyerId: json['Buyer_ID'],
      quantity: json['Quantity'],
      totalAmount: double.parse(json['Total_Amount'].toString()),
      paymentMethod: json['Payment_Method'],
      paymentStatus: json['Payment_Status'],
      status: json['Status'],
      dateOrdered: DateTime.parse(json['Date_Ordered']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Order_ID': orderId,
      'Product_ID': productId,
      'Seller_ID': sellerId,
      'Shop_ID': shopId,
      'Buyer_ID': buyerId,
      'Quantity': quantity,
      'Total_Amount': totalAmount,
      'Payment_Method': paymentMethod,
      'Payment_Status': paymentStatus,
      'Status': status,
      'Date_Ordered': dateOrdered.toIso8601String(),
    };
  }
} 