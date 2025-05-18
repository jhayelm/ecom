class AdminAccount {
  final int? adminId;
  final String firstname;
  final String? middleInitial;
  final String lastname;
  final String? suffix;
  final String email;
  final String password;
  final String status;
  final String role;
  final DateTime timestamp;

  AdminAccount({
    this.adminId,
    required this.firstname,
    this.middleInitial,
    required this.lastname,
    this.suffix,
    required this.email,
    required this.password,
    required this.status,
    required this.role,
    required this.timestamp,
  });

  factory AdminAccount.fromJson(Map<String, dynamic> json) {
    return AdminAccount(
      adminId: json['Admin_ID'],
      firstname: json['Firstname'],
      middleInitial: json['Middle_Initial'],
      lastname: json['Lastname'],
      suffix: json['Suffix'],
      email: json['Email'],
      password: json['Password'],
      status: json['Status'],
      role: json['Role'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'Admin_ID': adminId,
      'Firstname': firstname,
      'Middle_Initial': middleInitial,
      'Lastname': lastname,
      'Suffix': suffix,
      'Email': email,
      'Password': password,
      'Status': status,
      'Role': role,
      'timestamp': timestamp.toIso8601String(),
    };
  }
} 