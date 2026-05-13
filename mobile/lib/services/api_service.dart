import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/estacion.dart';

const String baseUrl = "http://10.0.2.2:8000";

class AuthService {
  Future<bool> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/token'),
      body: {'username': username, 'password': password},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('jwt_token', data['access_token']);
      return true;
    }
    return false;
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token');
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
  }
}

class ApiService {
  Future<List<Estacion>> fetchEstaciones() async {
    final response = await http.get(Uri.parse('$baseUrl/estaciones/'));
    if (response.statusCode == 200) {
      List<dynamic> body = jsonDecode(response.body);
      return body.map((item) => Estacion.fromJson(item)).toList();
    }
    throw Exception('Error al cargar estaciones');
  }

  Future<bool> crearEstacion(String nombre, String ubicacion) async {
    final token = await AuthService().getToken();
    
    int tempId = DateTime.now().millisecondsSinceEpoch ~/ 1000; 

    final response = await http.post(
      Uri.parse('$baseUrl/estaciones/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'id': tempId,        
        'nombre': nombre,
        'ubicacion': ubicacion
      }),
    );
    
    return response.statusCode == 201 || response.statusCode == 200;
  }
}

Future<List<Estacion>> fetchEstaciones() async {
  try {
    final response = await http.get(Uri.parse('$baseUrl/estaciones/'))
      .timeout(const Duration(seconds: 5)); // Evita esperas infinitas

  if (response.statusCode == 200) {
    List jsonResponse = json.decode(response.body);
    return jsonResponse.map((data) => Estacion.fromJson(data)).toList();
  } else {
  throw Exception('Error del servidor: ${response.statusCode}');
  }
  } catch (e) {
// Esto evita que la App se cierre inesperadamente
    throw Exception('No se pudo conectar con SMAT. ¿Está el servidor activo?');
  }
}