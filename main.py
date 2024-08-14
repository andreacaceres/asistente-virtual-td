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
import pyperclip

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import subprocess as sub
import webbrowser as web

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    
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

def abrir_aplicacion_mac(nombre_aplicacion):
  os.system(f"open -a '{nombre_aplicacion}'")

def abrir_aplicacion_win(nombre_aplicacion):
  os.system(f"start {nombre_aplicacion}.exe")

def realizar_calculo(operacion):
    try:
        # Evalúa la operación de manera segura
        resultado = eval(operacion)
        return f"El resultado de {operacion} es {resultado}."
    except Exception as e:
        return "Lo siento, no pude realizar el cálculo. Asegúrate de que la operación es válida."
      
def establecer_temporizador(segundos):
    hablar(f"Temporizador establecido para {segundos} segundos.", motor_voces)
    time.sleep(segundos)
    hablar("¡El tiempo ha terminado!", motor_voces)
    
def leer_portapapeles(motor):
    contenido = pyperclip.paste()
    if contenido:
        hablar(f"El contenido del portapapeles es: {contenido}", motor)
        print(f"[*] Leyendo portapapeles: {contenido}")
    else:
        hablar("El portapapeles está vacío.", motor)
        print("[*] El portapapeles está vacío.")
        
        
# def ajustar_volumen_windows(nivel):
#     devices = AudioUtilities.GetSpeakers()
#     interface = devices.Activate(
#         IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#     volume = cast(interface, POINTER(IAudioEndpointVolume))
    
#     # Convertimos el nivel de 0 a 100 en un valor entre 0.0 y 1.0
#     volumen_scalar = nivel / 100.0
#     volume.SetMasterVolumeLevelScalar(volumen_scalar, None)
#     print(f"[*] Volumen ajustado al {nivel}%.")
        
        
def reducir_aumentar_volumen_windows(valor, reduccion=False):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    # Obtener el volumen actual
    volumen_actual = volume.GetMasterVolumeLevelScalar() * 100
    
    # Calcular el nuevo volumen
    if reduccion:
      nuevo_volumen = max(0, volumen_actual - valor)
    else:
      nuevo_volumen = min(100, volumen_actual + valor)
    
    # Convertimos el nivel de 0 a 100 en un valor entre 0.0 y 1.0
    volumen_scalar = nuevo_volumen / 100.0
    volume.SetMasterVolumeLevelScalar(volumen_scalar, None)
    
    print(f"[*] Volumen ajustado a {nuevo_volumen}%.")
    logging.debug(f'[*] Volumen ajustado a {nuevo_volumen}%.')
        
        
# programa principal
motor_voces = pyttsx4.init()
voces = motor_voces.getProperty('voices')
motor_voces.setProperty('voice', voces[1].id)
hablar('Hola, me llamo Viernes', motor_voces)
# Variables para Spotify
client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'

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
    
  elif 'spotify' in comando and activado:
    # 2. Reproducir una canción en Spotify (reproduce nombre_canción [de artista] en Spotify)
    logging.debug('[+] %s', comando)
    music = comando.replace('reproduce', '').replace('en spotify', '')
    song_artist = music.split(" de ")
    song = song_artist[0].lstrip()
    artist = song_artist[1].lstrip()
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))
    result = sp.search(artist)
    for i in range(0, len(result["tracks"]["items"])):
      name_song = result["tracks"]["items"][i]["name"].lower()
      if song.lower() in name_song:
        web.open(result["tracks"]["items"][i]["uri"])
        sleep(5)
        pyautogui.press("enter")
        break
    print('[*] Reproduciendo canción ...')
    logging.debug('[*] Reproduciendo canción.')
    activado = False
    
  elif 'youtube' in comando and activado:
    # 3. Reproducir un vídeo en YouTube (reproduce nombre_vídeo en YouTube)
    logging.debug('[+] %s', comando)
    music = comando.replace('reproduce', '')
    pywhatkit.playonyt(music)
    print('[*] Reproduciendo video ...')
    logging.debug('[*] Reproduciendo video.')
    activado = False
    
  elif comando.startswith('abre') and activado:
    # 4. Abre una aplicación (abre nombre_aplicación)
    logging.debug('[+] %s', comando)
    app = comando.replace('abre', '')
    print('[*] Abriendo aplicación ...')
    abrir_aplicacion_mac(app)
    # Para windows
    # abrir_aplicacion_win(app)
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
    
    # pyautogui.press('volumedown', 70)
    
    #windows
    reducir_aumentar_volumen_windows(10, reduccion=True)
    
    print('[*] Bajando el volumen 10 unidades ...')
    logging.debug('[*] Bajando el volumen 10 unidades.')
    activado = False
    
  elif comando.startswith('sube') and activado:
    # 5. Subir, bajar, configurar nivel volumen (subir/bajar volumen, poner volumen en tanto, silencio/quitar silencio)
    logging.debug('[+] %s', comando)
    
    # pyautogui.press('volumeup', 70)
    
    #windows
    reducir_aumentar_volumen_windows(10, reduccion=False)
    
    print('[*] Subiendo el volumen 10 unidades ...')
    logging.debug('[*] Subiendo el volumen 10 unidades.')
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
    resultado = '[*] La hora es: ', hora
    hablar(resultado, motor_voces)
    print('[*] La hora es: ', hora)
    logging.debug('[*] La hora es: [%s]', hora)
    activado = False
      
  elif comando.startswith('calcula') and activado:
      logging.debug('[+] %s', comando)
      operacion = comando.replace('calcula', '').strip()
      resultado = realizar_calculo(operacion)
      hablar(resultado, motor_voces)
      print('[*] ', resultado)
      logging.debug('[*] Realizó cálculo: %s', operacion)
      activado = False
      
  elif comando.startswith('temporizador') and activado:
      logging.debug('[+] %s', comando)
      try:
          segundos = int(comando.replace('temporizador', '').strip())
          establecer_temporizador(segundos)
          logging.debug('[*] Temporizador establecido para %s segundos.', segundos)
      except ValueError:
          hablar("Lo siento, no entendí el tiempo. Por favor, especifica en segundos.", motor_voces)
      activado = False
      
  elif comando == "lee portapapeles" and activado:
      logging.debug('[+] %s', comando)
      leer_portapapeles(motor_voces)
      logging.debug('[*] Leyó el portapapeles.')
      activado = False
      
  else:
    logging.debug('[!] %s', comando)
