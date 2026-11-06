# Tarea 6 — Optimización de rutas de reparto

Implementación dual de un optimizador de rutas con algoritmo voraz y control de
capacidad. El mismo motor lógico está resuelto en Python (interfaz gráfica) y en
Java (consola con validaciones y persistencia).

## Contenido

| Archivo | Descripción |
| --- | --- |
| `sistema_rutas/main.py` | Aplicación de escritorio con Tkinter y Matplotlib. |
| `java/Rutas.java` | Programa de consola con ArrayList, try-catch y archivo de reporte. |
| `java/paradas.txt` | Datos de entrada; incluye una línea inválida para probar la validación. |

## Requisitos

- Python 3.10 o superior con Tkinter y Matplotlib.
- Java 17 o superior.

## Ejecución

```bash
cd sistema_rutas
python main.py
```

```bash
cd java
javac Rutas.java
java -Dfile.encoding=UTF-8 Rutas
```

La aplicación de Python parte con seis paradas de ejemplo. El programa de Java
lee `paradas.txt` y guarda `reporte_rutas.txt` en la misma carpeta.

## Resultado de referencia

- 6 paradas válidas y 98 paquetes.
- Ruta de 51.25 km en 2 viajes.
- Costo estimado: 38.43 USD (tarifa de 0.75 USD/km).
