class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;
  final double? ultimoValor; // <-- Nuevo campo para el Reto Mobile

  Estacion({
    required this.id, 
    required this.nombre, 
    required this.ubicacion,
    this.ultimoValor,
  });

  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'],
      nombre: json['nombre'],
      ubicacion: json['ubicacion'],
      // Parseo seguro: busca posibles nombres que use tu backend y lo convierte a double
      ultimoValor: (json['ultimoValor'] ?? json['ultimo_valor'] ?? json['valor'])?.toDouble(),
    );
  }
}