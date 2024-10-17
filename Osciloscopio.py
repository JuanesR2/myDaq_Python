# archivo: read_daq_plot.py

import nidaqmx
from nidaqmx.constants import AcquisitionType
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time

class DAQReader:
    def __init__(self, device_name, channels, sample_rate=1000, buffer_size=1000):
        """
        Inicializa el lector DAQ.

        :param device_name: Nombre del dispositivo DAQ (e.g., 'myDAQ1')
        :param channels: Lista de canales analógicos a leer (e.g., ['ai0', 'ai1'])
        :param sample_rate: Tasa de muestreo en Hz
        :param buffer_size: Número de muestras en el buffer
        """
        self.device_name = device_name
        self.channels = channels
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.data = {channel: np.zeros(buffer_size) for channel in channels}
        self.running = False
        self.task = None
        self.lock = threading.Lock()

    def start(self):
        """Inicia la lectura de datos."""
        self.running = True
        self.task = nidaqmx.Task()
        try:
            for channel in self.channels:
                self.task.ai_channels.add_ai_voltage_chan(f"{self.device_name}/{channel}")

            self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate,
                                                 sample_mode=AcquisitionType.CONTINUOUS,
                                                 samps_per_chan=self.buffer_size)

            self.task.start()
            self.thread = threading.Thread(target=self.read_data, daemon=True)
            self.thread.start()
            print("Inicio de la tarea de lectura DAQ.")
        except nidaqmx.DaqError as e:
            print(f"Error al iniciar la tarea DAQ: {e}")
            self.stop()
        except Exception as e:
            print(f"Error inesperado: {e}")
            self.stop()

    def read_data(self):
        """Lee los datos continuamente en un hilo separado."""
        while self.running:
            try:
                raw_data = self.task.read(number_of_samples_per_channel=self.buffer_size)
                with self.lock:
                    for idx, channel in enumerate(self.channels):
                        # Actualizar los datos desplazando y agregando nuevas muestras
                        self.data[channel] = np.roll(self.data[channel], -self.buffer_size)
                        self.data[channel][-self.buffer_size:] = raw_data[idx]
                time.sleep(0.01)  # Ajusta según sea necesario
            except nidaqmx.DaqError as e:
                print(f"Error leyendo datos: {e}")
                self.stop()
            except Exception as e:
                print(f"Error inesperado durante la lectura: {e}")
                self.stop()

    def get_data(self):
        """Obtiene una copia de los datos actuales."""
        with self.lock:
            return {channel: self.data[channel].copy() for channel in self.channels}

    def stop(self):
        """Detiene la lectura de datos."""
        self.running = False
        if self.task:
            try:
                self.task.stop()
                self.task.close()
                print("Tarea DAQ detenida y cerrada.")
            except nidaqmx.DaqError as e:
                print(f"Error al detener la tarea DAQ: {e}")
            except Exception as e:
                print(f"Error inesperado al cerrar la tarea: {e}")

def listar_dispositivos():
    """Lista los dispositivos DAQ disponibles."""
    system = nidaqmx.system.System.local()
    devices = system.devices
    if not devices:
        print("No se encontraron dispositivos NI-DAQmx conectados.")
    else:
        print("Dispositivos disponibles:")
        for device in devices:
            print(f"- {device.name}")

def main():
    # Listar dispositivos disponibles
    listar_dispositivos()

    # Configuración del DAQReader
    DEVICE_NAME = 'myDAQ1'  # Actualiza esto según el nombre correcto de tu dispositivo
    CHANNELS = ['ai0', 'ai1']  # Lista de canales a leer
    SAMPLE_RATE = 1000  # Hz
    BUFFER_SIZE = 1000  # Número de muestras

    # Inicializar el lector DAQ
    daq_reader = DAQReader(device_name=DEVICE_NAME, channels=CHANNELS,
                           sample_rate=SAMPLE_RATE, buffer_size=BUFFER_SIZE)
    daq_reader.start()

    # Configuración de Matplotlib
    plt.style.use('default')  # Cambiado de 'seaborn' a 'default' para evitar errores
    fig, ax = plt.subplots()
    lines = {}
    for channel in CHANNELS:
        line, = ax.plot([], [], label=channel)
        lines[channel] = line

    # Ajustar los límites de los ejes
    ax.set_xlim(-BUFFER_SIZE/SAMPLE_RATE, 0)  # Últimos BUFFER_SIZE muestras
    ax.set_ylim(-10, 10)  # Ajusta según tus señales
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Voltaje (V)')
    ax.set_title('Entradas Analógicas DAQ en Tiempo Real')
    ax.legend()

    def init():
        for line in lines.values():
            line.set_data([], [])
        return lines.values()

    def animate(frame):
        data = daq_reader.get_data()
        t = np.linspace(-BUFFER_SIZE/SAMPLE_RATE, 0, BUFFER_SIZE)
        for channel in CHANNELS:
            lines[channel].set_data(t, data[channel])
        
       # Establecer el eje x para mostrar 4 ciclos de la señal de 60 Hz
        ax.set_xlim(-0.0667, 0)
        # Establecer el eje y para mostrar voltajes entre -3.3 V y 5 V
        #ax.set_ylim(-3.3, 5)


        

        return lines.values()

    ani = animation.FuncAnimation(fig, animate, init_func=init,
                                  interval=100, blit=True)

    try:
        plt.show()
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")
    finally:
        daq_reader.stop()

if __name__ == "__main__":
    main()
