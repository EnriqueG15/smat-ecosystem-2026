import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart'; 

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    // 1. Encendemos el feedback visual antes de la petición
    setState(() => _isLoading = true);
    
    try {
      bool success = await AuthService().login(
        _usernameController.text,
        _passwordController.text,
      );
      
      // 2. Validamos que el widget siga en pantalla ANTES de usar context o setState
      if (!mounted) return;

      if (success) {
        // Redirige al Dashboard reemplazando la pantalla actual
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomePage()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error: Credenciales incorrectas o Servidor caído')),
        );
      }
    } catch (e) {
      // Capturamos cualquier error inesperado de red para que la app no se quede en blanco
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo conectar: $e')),
      );
    } finally {
      // 3. Apagamos el cargador de forma segura pase lo que pase
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Iniciar Sesión')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Usuario'),
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Contraseña'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            
            // Reto de Puesta a Punto: Feedback visual dinámico
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _login,
                    child: const Text('Ingresar'),
                  ),
          ],
        ),
      ),
    );
  }
}