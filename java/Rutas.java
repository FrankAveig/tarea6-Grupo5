import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Tarea 6 - Implementación en Java.
 *
 * Lee las paradas desde paradas.txt, valida cada línea, calcula la ruta con un
 * algoritmo voraz que respeta la capacidad del vehículo y guarda el reporte en
 * reporte_rutas.txt.
 *
 * Demuestra: ArrayList, try-catch específico, validación de tipos, bucles con
 * decisión y persistencia en archivo de texto.
 */
public class Rutas {

    static final int CAPACIDAD = 60;
    static final double TARIFA_KM = 0.75;

    /** Entidad inmutable con encapsulamiento. */
    static class Parada {
        private final String nombre;
        private final double x;
        private final double y;
        private final int paquetes;

        Parada(String nombre, double x, double y, int paquetes) {
            if (nombre == null || nombre.isBlank()) {
                throw new IllegalArgumentException("nombre vacío");
            }
            if (paquetes <= 0) {
                throw new IllegalArgumentException("paquetes debe ser mayor que cero");
            }
            if (paquetes > CAPACIDAD) {
                throw new IllegalArgumentException("una parada no puede superar " + CAPACIDAD + " paquetes");
            }
            this.nombre = nombre;
            this.x = x;
            this.y = y;
            this.paquetes = paquetes;
        }

        String getNombre() { return nombre; }
        double getX() { return x; }
        double getY() { return y; }
        int getPaquetes() { return paquetes; }

        double distanciaA(double otraX, double otraY) {
            return Math.hypot(x - otraX, y - otraY);
        }
    }

    static class Resultado {
        List<String[]> filas = new ArrayList<>();
        double total;
        int viajes;
    }

    public static void main(String[] args) {
        System.out.println("======================================================");
        System.out.println("   OPTIMIZACION DE RUTAS - GRUPO 5 (JAVA)");
        System.out.println("======================================================");

        List<Parada> paradas = cargar("paradas.txt");
        System.out.printf("Paradas validas: %d%n%n", paradas.size());

        if (paradas.size() < 2) {
            System.out.println("Se necesitan al menos dos paradas validas.");
            return;
        }

        Resultado resultado = optimizar(paradas);
        imprimir(resultado);
        guardar(resultado, paradas.size());
    }

    /** Lee y valida el archivo; las líneas con error se informan y se omiten. */
    static List<Parada> cargar(String archivo) {
        List<Parada> lista = new ArrayList<>();
        try (BufferedReader lector = new BufferedReader(
                new FileReader(archivo, StandardCharsets.UTF_8))) {
            String linea;
            int numero = 0;
            while ((linea = lector.readLine()) != null) {
                numero++;
                if (linea.isBlank()) {
                    continue;
                }
                try {
                    String[] partes = linea.split(";");
                    if (partes.length != 4) {
                        throw new IllegalArgumentException("se esperaban 4 campos");
                    }
                    lista.add(new Parada(
                            partes[0].trim(),
                            Double.parseDouble(partes[1].trim()),
                            Double.parseDouble(partes[2].trim()),
                            Integer.parseInt(partes[3].trim())
                    ));
                } catch (NumberFormatException error) {
                    System.out.printf("Linea %d ignorada: valor numerico invalido.%n", numero);
                } catch (IllegalArgumentException error) {
                    System.out.printf("Linea %d ignorada: %s.%n", numero, error.getMessage());
                }
            }
        } catch (IOException error) {
            System.out.println("No se pudo leer " + archivo + ": " + error.getMessage());
        }
        return lista;
    }

    /** Algoritmo voraz: siempre la parada más cercana, con retorno por capacidad. */
    static Resultado optimizar(List<Parada> paradas) {
        Resultado resultado = new Resultado();
        List<Parada> pendientes = new ArrayList<>(paradas);
        double actualX = 0, actualY = 0;
        int carga = 0, viaje = 1, orden = 1;
        double total = 0;

        while (!pendientes.isEmpty()) {
            Parada cercana = pendientes.get(0);
            double menor = cercana.distanciaA(actualX, actualY);
            for (int i = 1; i < pendientes.size(); i++) {
                double distancia = pendientes.get(i).distanciaA(actualX, actualY);
                if (distancia < menor) {
                    menor = distancia;
                    cercana = pendientes.get(i);
                }
            }

            if (carga + cercana.getPaquetes() > CAPACIDAD) {
                double tramo = Math.hypot(actualX, actualY);
                total += tramo;
                resultado.filas.add(new String[]{
                        String.valueOf(viaje), String.valueOf(orden), "Base (regreso)",
                        String.format(Locale.US, "%.2f", tramo), "-",
                        String.format(Locale.US, "%.2f", total)
                });
                actualX = 0;
                actualY = 0;
                carga = 0;
                viaje++;
                orden = 1;
                continue;
            }

            double tramo = cercana.distanciaA(actualX, actualY);
            total += tramo;
            carga += cercana.getPaquetes();
            resultado.filas.add(new String[]{
                    String.valueOf(viaje), String.valueOf(orden), cercana.getNombre(),
                    String.format(Locale.US, "%.2f", tramo), String.valueOf(carga),
                    String.format(Locale.US, "%.2f", total)
            });
            actualX = cercana.getX();
            actualY = cercana.getY();
            pendientes.remove(cercana);
            orden++;
        }

        double regreso = Math.hypot(actualX, actualY);
        total += regreso;
        resultado.filas.add(new String[]{
                String.valueOf(viaje), String.valueOf(orden), "Base (regreso)",
                String.format(Locale.US, "%.2f", regreso), "-",
                String.format(Locale.US, "%.2f", total)
        });

        resultado.total = total;
        resultado.viajes = viaje;
        return resultado;
    }

    static void imprimir(Resultado resultado) {
        System.out.println("Ruta calculada:");
        System.out.printf("%-6s %-6s %-22s %8s %8s %10s%n",
                "Viaje", "Orden", "Parada", "km", "Carga", "Acum.");
        System.out.println("------------------------------------------------------------------");
        for (String[] fila : resultado.filas) {
            System.out.printf("%-6s %-6s %-22s %8s %8s %10s%n",
                    fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]);
        }
        System.out.println("------------------------------------------------------------------");
        System.out.printf(Locale.US, "Distancia total: %.2f km%n", resultado.total);
        System.out.printf(Locale.US, "Costo estimado:  $%.2f%n", resultado.total * TARIFA_KM);
        System.out.printf("Viajes: %d%n", resultado.viajes);
    }

    static void guardar(Resultado resultado, int paradas) {
        try (PrintWriter escritor = new PrintWriter(
                new FileWriter("reporte_rutas.txt", StandardCharsets.UTF_8))) {
            escritor.println("REPORTE DE OPTIMIZACION DE RUTAS - GRUPO 5");
            escritor.printf("Paradas validas: %d%n", paradas);
            escritor.printf("Capacidad del vehiculo: %d paquetes%n", CAPACIDAD);
            escritor.println();
            escritor.printf("%-6s %-6s %-22s %8s %8s %10s%n",
                    "Viaje", "Orden", "Parada", "km", "Carga", "Acum.");
            for (String[] fila : resultado.filas) {
                escritor.printf("%-6s %-6s %-22s %8s %8s %10s%n",
                        fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]);
            }
            escritor.println();
            escritor.printf(Locale.US, "Distancia total: %.2f km%n", resultado.total);
            escritor.printf(Locale.US, "Costo estimado:  $%.2f%n", resultado.total * TARIFA_KM);
            escritor.printf("Viajes: %d%n", resultado.viajes);
            System.out.println("\nReporte guardado en reporte_rutas.txt");
        } catch (IOException error) {
            System.out.println("No se pudo guardar el reporte: " + error.getMessage());
        }
    }
}
