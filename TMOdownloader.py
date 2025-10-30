from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from getpass import getpass  # Importar getpass para ocultar la contraseña

# Configuración de opciones para Brave
options = Options()

# Ruta al navegador Brave
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Ruta a Brave
options.binary_location = brave_path  # Le decimos a Selenium que use Brave en lugar de Chrome

# Configurar el WebDriver para usar ChromeDriver con Brave
options.add_argument("--headless")  # Si no quieres que se vea el navegador (modo sin interfaz gráfica)
options.add_argument("--no-sandbox")  # Para evitar posibles errores con el sandbox en algunos sistemas
options.add_argument("--disable-dev-shm-usage")  # Recomendado en contenedores Docker

# Iniciar el WebDriver con las opciones configuradas
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Función para navegar a una página seleccionada
def navegar_a_pagina(pagina):
    if pagina == "1":
        url = "https://zonatmo.com/profile/read"
        nombre_archivo = "libros_leidos.txt"
    elif pagina == "2":
        url = "https://zonatmo.com/profile/pending"
        nombre_archivo = "libros_pendientes.txt"
    elif pagina == "3":
        url = "https://zonatmo.com/profile/follow"
        nombre_archivo = "libros_seguidos.txt"
    elif pagina == "4":
        url = "https://zonatmo.com/profile/wish"
        nombre_archivo = "libros_deseados.txt"
    elif pagina == "5":
        url = "https://zonatmo.com/profile/have"
        nombre_archivo = "libros_tengo.txt"
    else:
        print("Opción no válida.")
        return None, None

    driver.get(url)
    return url, nombre_archivo

# Función principal
def extraer_libros():
    try:
        # Acceder a la página de login
        login_url = "https://zonatmo.com/login"
        driver.get(login_url)

        # Espera explícita para que el token CSRF esté presente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "csrf-token")))

        # Obtener el token CSRF
        csrf_token_meta = driver.find_element("name", "csrf-token")
        csrf_token = csrf_token_meta.get_attribute("content")
        print(f"Token CSRF: {csrf_token}")

        # Esperar hasta que el campo de usuario esté presente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))  # Usamos el name="email"

        # Solicitar al usuario el correo y la contraseña
        correo = input("Introduce tu correo electrónico: ")
        contrasena = getpass("Introduce tu contraseña: ")  # Usamos getpass para ocultar la entrada

        # Realizar login
        usuario_input = driver.find_element("name", "email")  # Ahora el campo es email
        contrasena_input = driver.find_element("name", "password")  # El campo de contraseña es password

        usuario_input.send_keys(correo)  # Ingresar el correo proporcionado por el usuario
        contrasena_input.send_keys(contrasena)  # Ingresar la contraseña proporcionada por el usuario

        # Crear el formulario de login y enviarlo
        login_button = driver.find_element("xpath", "//button[@type='submit']")  # Ajusta según el botón
        login_button.click()

        # Esperar para verificar que se haya hecho login correctamente
        WebDriverWait(driver, 10).until(EC.title_contains("ZonaTMO"))  # O algún título relacionado con el login

        # Menú de selección de página
        print("Selecciona la página de la cual deseas extraer los libros:")
        print("1. Libros Leídos")
        print("2. Libros Pendientes")
        print("3. Libros Seguidos")
        print("4. Libros en la Lista de Deseos")
        print("5. Libros que Tengo")
        seleccion = input("Ingresa el número de la opción deseada: ")

        # Navegar a la página seleccionada
        url_pagina, nombre_archivo = navegar_a_pagina(seleccion)
        if url_pagina is None:
            return  # Si la opción no es válida, terminamos la función

        print(f"Navegando a: {url_pagina}")

        # Crear archivo txt para guardar los títulos
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Títulos extraídos de la página: {url_pagina}\n\n")  # Escribir el encabezado en el archivo

            # Esperar a que la página cargue completamente (espera los libros)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h4.text-truncate")))

            # Iterar a través de las páginas de libros
            page = 1  # Página inicial
            while True:
                print(f"Extrayendo libros de la página {page}...")

                # Obtener los títulos de los libros de la página actual
                libros = driver.find_elements("css selector", "h4.text-truncate")  # Buscamos los <h4> con la clase 'text-truncate'

                # Mostrar los títulos de los libros
                if libros:
                    for libro in libros:
                        titulo = libro.get_attribute("title")  # Extraemos el título desde el atributo 'title'
                        archivo.write(f"{titulo}\n")  # Guardamos el título en el archivo
                        print(titulo)
                else:
                    print("No se encontraron títulos de libros en esta página.")
                    archivo.write("No se encontraron títulos de libros en esta página.\n")

                # Intentar obtener el enlace de la siguiente página
                try:
                    # Esperar a que el enlace de 'Siguiente' esté presente
                    siguiente_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[rel='next']")))

                    siguiente_url = siguiente_btn.get_attribute("href")  # Obtenemos la URL del siguiente enlace
                    if not siguiente_url:
                        print("No se pudo encontrar la URL de la siguiente página.")
                        archivo.write("No se pudo encontrar la URL de la siguiente página.\n")
                        break  # Salir si no hay siguiente página
                    driver.get(siguiente_url)  # Navegar a la siguiente página usando la URL
                    page += 1  # Incrementar el número de página
                    print(f"Cargando la siguiente página: {siguiente_url}")
                    time.sleep(3)  # Esperar a que cargue la nueva página
                except Exception as e:
                    print(f"No se pudo encontrar el botón de 'Siguiente' o hemos llegado al final: {e}")
                    archivo.write(f"No se pudo encontrar el botón de 'Siguiente' o hemos llegado al final: {e}\n")
                    break  # Romper el bucle si no hay más páginas

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        print("Detalles del error:", e)

    finally:
        # Cerrar el navegador al final
        driver.quit()

# Llamar a la función principal para ejecutar el script
extraer_libros()
