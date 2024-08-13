# imports
import speech_recognition as sr
import pyaudio
import pyttsx4
import pyjokes
import pyautogui
import os
import pywhatkit
from datetime import datetime
import time
import logging

logging.basicConfig(filename='std.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.DEBUG)

# functions
def hablar(texto, motor):
  motor.say(texto)
  # Tuve que comentar esta linea porque daba problemas en MacBookPro M2
  # motor.runAndWait()
  # Las siguientes lineas hace que luego que el asistente comience hablar no se cierre de manera abrupta.
  motor.startLoop(False)
  motor.iterate()
  motor.endLoop()

def escuchar():
  listener = sr.Recognizer()
  listener.energy_threshold = 17500
  comando = ''
  try:
    with sr.Microphone() as source:
      print('[*] Escuchando ...')
      listener.adjust_for_ambient_noise(source)
      captura = listener.listen(source)
      comando = listener.recognize_google(captura, language="es-ES")
  except Exception as e:
    print('[*] Error. Algo paso: ', str(e))
  return comando.lower()

# programa principal
motor_voces = pyttsx4.init()
voces = motor_voces.getProperty('voices')
motor_voces.setProperty('voice', voces[32].id)
hablar('Hola, me llamo Viernes', motor_voces)
activado = False
while True:
  comando = escuchar()
  print('Comando: ', comando)
  if comando == 'hola viernes':
    print('[*] Beep!! Estoy listo para ejecutar un comando...')
    activado = True
  elif comando == 'dime un chiste' and activado:
    # 1. Decir un chiste (dime un chiste)
    logging.debug('[+] %s', comando)
    hablar(pyjokes.get_joke(language='es', category='all'), motor_voces)
    logging.debug('[*] El asistente contó chiste.')
    activado = False
  elif comando.startswith('reproduce') and activado:
    # 2. Reproducir una canción en Spotify (reproduce nombre_canción [de artista] en Spotify)
    logging.debug('[+] %s', comando)
    print('[*] Reproduciendo canción ...')
    logging.debug('[*] Reproduciendo canción.')
    activado = False
  elif comando.startswith('reproduce') and activado:
    # 3. Reproducir un vídeo en YouTube (reproduce nombre_vídeo en YouTube)
    logging.debug('[+] %s', comando)
    music = comando.replace('reproduce', '')
    pywhatkit.playonyt(music)
    print('[*] Reproduciendo video ...')
    logging.debug('[*] Reproduciendo video.')
    activado = False
  elif comando == "abre" and activado:
    # 4. Abre una aplicación (abre nombre_aplicación)
    # here comes the code.
    logging.debug('[+] %s', comando)
    print('[*] Abriendo aplicación ...')
    logging.debug('[*] Abriendo aplicación.')
    activado = False
  elif comando == 'silencio' and activado:
    #  5. Subir, bajar, configurar nivel volumen (subir/bajar volumen, poner volumen en tanto, silencio/quitar silencio)
    logging.debug('[+] %s', comando)
    pyautogui.hotkey('volumemute')
    print('[*] Silencio ...')
    logging.debug('[*] Silencio.')
    activado = False
  elif comando.startswith('baja') and activado:
    # 5. Subir, bajar, configurar nivel volumen (subir/bajar volumen, poner volumen en tanto, silencio/quitar silencio)
    logging.debug('[+] %s', comando)
    pyautogui.press('volumedown', 70)
    print('[*] Bajando el volumen al 70% ...')
    logging.debug('[*] Bajando el volumen al 70%.')
    activado = False
  elif comando.startswith('sube') and activado:
    # 5. Subir, bajar, configurar nivel volumen (subir/bajar volumen, poner volumen en tanto, silencio/quitar silencio)
    logging.debug('[+] %s', comando)
    pyautogui.press('volumeup', 70)
    print('[*] Subiendo el volumen al 70% ...')
    logging.debug('[*] Subiendo el volumen al 70%.')
    activado = False
  elif comando == "imprime pantalla" and activado:
    # A. imprime pantalla
    logging.debug('[+] %s', comando)
    screenshot = pyautogui.screenshot()
    carpeta_contenedora = 'screenshots'
    if not os.path.exists(carpeta_contenedora):
      os.makedirs(carpeta_contenedora)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_').replace(':', '_')
    screenshot.save(f'{carpeta_contenedora}/{now}_screenshot.png')
    print('[*] Captura de pantalla en ', carpeta_contenedora)
    logging.debug('[*] Capturo pantalla.')
    activado = False
  elif comando == "dime la hora" and activado:
    # B. Dime la hora actual
    logging.debug('[+] %s', comando)
    hora = datetime.now().strftime('%H:%M %p')
    print('[*] La hora es: ', hora)
    logging.debug('[*] La hora es: [%s]', hora)
    activado = False
  else:
    logging.debug('[!] %s', comando)
