# DAQ Realtime Plotter con Python y NI-DAQmx 📊⚡

Este repositorio contiene una aplicación en Python para la adquisición y visualización en tiempo real de señales analógicas desde un dispositivo NI-DAQmx (como **myDAQ** o **USB-6001**), usando `nidaqmx`, `matplotlib` y `numpy`.

---

## 🚀 Descripción

El programa:

- Detecta los dispositivos DAQ conectados.
- Lee datos analógicos en tiempo real desde múltiples canales (`ai0`, `ai1`, etc.).
- Muestra una gráfica en vivo usando `matplotlib.animation`.
- Mantiene un buffer circular para visualizar los datos más recientes.
- Es compatible con señales de 60 Hz y puede mostrar hasta 4 ciclos de la señal.

---

## 🧰 Requisitos

- Python 3.8 o superior
- NI-DAQmx driver instalado (y configurado)
- Módulos de Python:

```bash
pip install nidaqmx numpy matplotlib
```

---

## ⚙️ Configuración

Dentro de `read_daq_plot.py`, puedes configurar:

```python
DEVICE_NAME = 'myDAQ1'       # Nombre del dispositivo DAQ
CHANNELS = ['ai0', 'ai1']    # Canales analógicos a visualizar
SAMPLE_RATE = 1000           # Hz
BUFFER_SIZE = 1000           # Número de muestras por canal
```

Asegúrate de que el nombre del dispositivo coincida con el listado por NI MAX o el comando interno `listar_dispositivos()`.

---

## ▶️ Ejecución

```bash
python read_daq_plot.py
```

Aparecerá una ventana con la gráfica de voltajes de los canales seleccionados, actualizándose en tiempo real.

---

## 📐 Detalles técnicos

- **Adquisición continua:** modo `CONTINUOUS` con `cfg_samp_clk_timing`.
- **Sin bloqueo:** uso de hilos (`threading.Thread`) para la lectura asincrónica.
- **Buffer circular:** usando `np.roll` para desplazar los datos y mantener las muestras más recientes.
- **Gráfica optimizada:** `matplotlib.animation.FuncAnimation` para animaciones suaves.

---

## 🛑 Salida controlada

El script se detiene correctamente al cerrar la ventana o presionar `Ctrl+C`, cerrando la tarea DAQ y liberando recursos.

---

## 📷 Captura de pantalla (opcional)

*Puedes incluir aquí una imagen de la gráfica en tiempo real para mostrar cómo se ve.*

---

## 📄 Licencia

MIT

---

## 👨‍💻 Autor

Juan Esteban Rodríguez Villada – 2025  
Universidad Tecnológica de Pereira  
```
