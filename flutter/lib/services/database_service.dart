import 'package:mysql1/mysql1.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  final _storage = const FlutterSecureStorage();

  Future<ConnectionSettings> _getConnectionSettings() async {
    // Try to get settings from secure storage, otherwise use defaults
    final host = await _storage.read(key: 'db_host') ?? 'localhost';
    final port = int.parse(await _storage.read(key: 'db_port') ?? '3306');
    final user = await _storage.read(key: 'db_user') ?? 'root';
    final password = await _storage.read(key: 'db_password') ?? '';
    final db = await _storage.read(key: 'db_name') ?? 'fenamaz';

    return ConnectionSettings(
      host: host,
      port: port,
      user: user,
      password: password,
      db: db,
    );
  }

  Future<void> updateConnectionSettings({
    String? host,
    int? port,
    String? user,
    String? password,
    String? db,
  }) async {
    if (host != null) await _storage.write(key: 'db_host', value: host);
    if (port != null) await _storage.write(key: 'db_port', value: port.toString());
    if (user != null) await _storage.write(key: 'db_user', value: user);
    if (password != null) await _storage.write(key: 'db_password', value: password);
    if (db != null) await _storage.write(key: 'db_name', value: db);
  }

  Future<MySqlConnection> getConnection() async {
    final settings = await _getConnectionSettings();

    try {
      final conn = await MySqlConnection.connect(settings);
      print('Connected to MySQL database');
      return conn;
    } catch (e) {
      print('Database connection error: $e');
      throw Exception('Failed to connect to database');
    }
  }

  Future<void> closeConnection(MySqlConnection connection) async {
    await connection.close();
  }
} 