class ProductImage {
  final int? productImageId;
  final int? productInfoId;
  final String? productImage;

  ProductImage({
    this.productImageId,
    this.productInfoId,
    this.productImage,
  });

  factory ProductImage.fromJson(Map<String, dynamic> json) {
    return ProductImage(
      productImageId: json['Product_Image_ID'],
      productInfoId: json['Product_Info_ID'],
      productImage: json['Product_Image'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Product_Image_ID': productImageId,
      'Product_Info_ID': productInfoId,
      'Product_Image': productImage,
    };
  }
} 