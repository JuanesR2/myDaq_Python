import nidaqmx
from nidaqmx.constants import AcquisitionType, RegenerationMode
from nidaqmx.stream_writers import AnalogMultiChannelWriter
import numpy as np
import time
import signal
import sys

def signal_handler(sig, frame):
    print('Programa terminado por el usuario.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Obtener la lista de dispositivos disponibles
system = nidaqmx.system.System.local()
dispositivos = list(system.devices)

if not dispositivos:
    print("No se encontraron dispositivos NI-DAQmx conectados.")
    sys.exit(1)
else:
    dispositivo = dispositivos[0].name
    print(f"Usando el dispositivo: {dispositivo}")

# Parámetros de la señal
frecuencia = 60  # Hz
amplitud = 3.3 / 2  # 3.3 Vpp -> amplitud pico de 1.65 V
desplazamiento = 1.65  # V (para centrar la señal en el rango de 0 V a 3.3 V)

# Configuración de muestreo
tasa_muestreo = 6000  # muestras por segundo
muestras_por_ciclo = int(tasa_muestreo / frecuencia)

# Generación de la señal de tiempo
muestras_a_escribir = muestras_por_ciclo * 10  # 10 ciclos de señal
t = np.linspace(0, muestras_a_escribir / tasa_muestreo, muestras_a_escribir, endpoint=False)

# Generación de las señales sinusoidales con offset
onda1 = amplitud * np.sin(2 * np.pi * frecuencia * t) + desplazamiento
onda2 = amplitud * np.sin(2 * np.pi * frecuencia * t + 2 * np.pi/3) + desplazamiento  # Desfase de 120 grados

# Organizar las señales en un arreglo para múltiples canales
datos = np.vstack((onda1, onda2))

try:
    with nidaqmx.Task() as tarea_ao:
        # Agregar dos canales de salida analógica
        tarea_ao.ao_channels.add_ao_voltage_chan(f"{dispositivo}/ao0")
        tarea_ao.ao_channels.add_ao_voltage_chan(f"{dispositivo}/ao1")

        # Configurar el reloj de muestreo
        tarea_ao.timing.cfg_samp_clk_timing(rate=tasa_muestreo, sample_mode=AcquisitionType.CONTINUOUS)

        # Permitir la regeneración del buffer
        tarea_ao.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION

        # Escribir datos en el buffer una vez
        escritor = AnalogMultiChannelWriter(tarea_ao.out_stream, auto_start=False)
        escritor.write_many_sample(datos)

        # Iniciar la tarea
        tarea_ao.start()

        print("Generando señales. Presiona Ctrl+C para detener.")

        # Esperar indefinidamente
        while True:
            time.sleep(1)

except KeyboardInterrupt:
    print('Programa terminado por el usuario.')
except Exception as e:
    print('Ocurrió un error: {}'.format(e))
finally:
    try:
        tarea_ao.stop()
        tarea_ao.close()
    except NameError:
        pass
    except Exception as e:
        print('Error al cerrar la tarea: {}'.format(e))
