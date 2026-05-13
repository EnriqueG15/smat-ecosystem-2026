import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/estacion.dart';
import 'screens/login_screen.dart'; 
import 'screens/add_estacion.dart'; 

void main() => runApp(const SMATApp());

class SMATApp extends StatelessWidget {
  const SMATApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: FutureBuilder<String?>(
        future: AuthService().getToken(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          }
          if (snapshot.hasData && snapshot.data != null) {
            return const HomePage();
          } else {
            return const LoginScreen();
          }
        },
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  final ApiService apiService = ApiService(); // Instancia para reutilizar en el CRUD

  @override
  void initState() {
    super.initState();
    futureEstaciones = apiService.fetchEstaciones();
  }

  Future<void> _refresh() async {
    setState(() {
      futureEstaciones = apiService.fetchEstaciones();
    });
    try {
      await futureEstaciones;
    } catch (_) {}
  }

  // --- PASO 3: Método para mostrar el Diálogo de Edición ---
  void _mostrarDialogoEdicion(Estacion estacion) {
    final nombreCtrl = TextEditingController(text: estacion.nombre);
    final ubicacionCtrl = TextEditingController(text: estacion.ubicacion);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Editar Estación"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nombreCtrl, decoration: const InputDecoration(labelText: "Nombre")),
            TextField(controller: ubicacionCtrl, decoration: const InputDecoration(labelText: "Ubicación")),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context), 
            child: const Text("Cancelar")
          ),
          ElevatedButton(
            onPressed: () async {
              // Llamada a la API para actualizar
              bool ok = await apiService.editarEstacion(
                estacion.id, 
                nombreCtrl.text, 
                ubicacionCtrl.text
              );
              if (ok && context.mounted) {
                Navigator.pop(context);
                _refresh(); // Refrescar la lista con los nuevos datos
              }
            },
            child: const Text("Guardar"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SMAT - Monitoreo Móvil'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar Sesión',
            onPressed: () async {
              await AuthService().logout(); 
              if (!context.mounted) return;
              
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
                (route) => false,
              );
            },
          )
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return const Center(child: Text('❌ Error de conexión o sesión expirada'));
          } else {
            return RefreshIndicator(
              onRefresh: _refresh, 
              child: ListView.builder(
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final est = snapshot.data![index];
                  
                  // --- RETO DE LA FASE MOBILE: Lógica de Colores ---
                  // Nota: Asegúrate de que tu modelo 'Estacion' tenga la propiedad del valor de lectura.
                  // Aquí uso 'est.ultimoValor' como ejemplo. Cámbialo por el nombre real de tu variable.
                  // Verde si es normal (< 50), Rojo si supera el umbral crítico (> 50).
                  final double valorLectura = est.ultimoValor ?? 0.0; 
                  final Color colorAlerta = (valorLectura < 50) ? Colors.green : Colors.red;

                  // --- PASO 2: Envolver el ListTile en un Dismissible ---
                  return Dismissible(
                    key: Key(est.id.toString()), // Identificador único requerido
                    direction: DismissDirection.endToStart, // Deslizar de derecha a izquierda
                    background: Container(
                      color: Colors.red,
                      alignment: Alignment.centerRight,
                      padding: const EdgeInsets.only(right: 20),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    onDismissed: (direction) async {
                      // Ejecutar la eliminación en el backend
                      bool ok = await apiService.eliminarEstacion(est.id);
                      if (ok && context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text("${est.nombre} eliminada")),
                        );
                        // Opcional pero recomendado: sincronizar la vista
                        _refresh();
                      }
                    },
                    child: ListTile(
                      leading: Icon(Icons.satellite_alt, color: colorAlerta), // Aplicamos color del Reto
                      title: Text(est.nombre),
                      subtitle: Text(est.ubicacion),
                      onTap: () => _mostrarDialogoEdicion(est), // Gatillamos el Paso 3 al tocar
                    ),
                  );
                },
              ),
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddEstacionScreen()),
          );
          
          if (result == true) {
            _refresh();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}