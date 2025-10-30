from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from getpass import getpass
import time


# 🧩 Función para seleccionar el navegador
def seleccionar_navegador():
    print("\nSelecciona el navegador que deseas usar:")
    print("1. Chrome")
    print("2. Brave")
    print("3. Firefox")
    opcion = input("Ingresa el número de la opción deseada: ")

    if opcion == "1":  # Chrome
        options = ChromeOptions()
        configurar_opciones_comunes(options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif opcion == "2":  # Brave
        options = ChromeOptions()
        configurar_opciones_comunes(options)
        # Ruta por defecto de Brave (ajústala si está en otro directorio)
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        options.binary_location = brave_path
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif opcion == "3":  # Firefox
        options = FirefoxOptions()
        configurar_opciones_comunes(options)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    else:
        print("Opción inválida. Usando Chrome por defecto.")
        options = ChromeOptions()
        configurar_opciones_comunes(options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.set_window_size(1280, 800)
    return driver


# 🧹 Configura opciones comunes (headless y sin logs)
def configurar_opciones_comunes(options):
    # Siempre sin ventana
    options.add_argument("--headless=new")

    # 🔇 Ocultar logs y mensajes de GPU/WebGL
    try:
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    except Exception:
        pass

    # ⚙️ Configuración extra
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-webgl")                  # Evita error de WebGL
    options.add_argument("--disable-software-rasterizer")    # Evita fallback SwiftShader


# 🧭 Función para navegar a una página seleccionada
def navegar_a_pagina(driver, pagina):
    paginas = {
        "1": ("https://zonatmo.com/profile/read", "libros_leidos.txt"),
        "2": ("https://zonatmo.com/profile/pending", "libros_pendientes.txt"),
        "3": ("https://zonatmo.com/profile/follow", "libros_seguidos.txt"),
        "4": ("https://zonatmo.com/profile/wish", "libros_deseados.txt"),
        "5": ("https://zonatmo.com/profile/have", "libros_tengo.txt")
    }
    return paginas.get(pagina, (None, None))


# 🧠 Función principal
def extraer_libros():
    driver = seleccionar_navegador()

    try:
        driver.get("https://zonatmo.com/login")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "csrf-token")))
        csrf_token_meta = driver.find_element("name", "csrf-token")
        csrf_token = csrf_token_meta.get_attribute("content")
        print(f"Token CSRF detectado: {csrf_token}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

        correo = input("Introduce tu correo electrónico: ")
        contrasena = getpass("Introduce tu contraseña: ")

        usuario_input = driver.find_element("name", "email")
        contrasena_input = driver.find_element("name", "password")

        usuario_input.send_keys(correo)
        contrasena_input.send_keys(contrasena)

        login_button = driver.find_element("xpath", "//button[@type='submit']")
        login_button.click()

        WebDriverWait(driver, 10).until(EC.title_contains("ZonaTMO"))

        print("\nSelecciona la página de la cual deseas extraer los libros:")
        print("1. Libros Leídos")
        print("2. Libros Pendientes")
        print("3. Libros Seguidos")
        print("4. Lista de Deseos")
        print("5. Libros que Tengo")
        seleccion = input("Ingresa el número de la opción deseada: ")

        url_pagina, nombre_archivo = navegar_a_pagina(driver, seleccion)
        if not url_pagina:
            print("Opción no válida.")
            return

        driver.get(url_pagina)
        print(f"Navegando a: {url_pagina}")

        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Títulos extraídos de la página: {url_pagina}\n\n")

            page = 1
            while True:
                print(f"\n📖 Extrayendo libros de la página {page}...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h4.text-truncate"))
                )

                libros = driver.find_elements("css selector", "h4.text-truncate")

                if libros:
                    for libro in libros:
                        titulo = libro.get_attribute("title")
                        archivo.write(f"{titulo}\n")
                        print(f" - {titulo}")
                else:
                    print("No se encontraron títulos de libros.")
                    break

                try:
                    siguiente_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[rel='next']"))
                    )
                    siguiente_url = siguiente_btn.get_attribute("href")
                    if not siguiente_url:
                        break
                    driver.get(siguiente_url)
                    page += 1
                    time.sleep(3)
                except Exception:
                    print("✅ Fin de las páginas.")
                    break

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    finally:
        driver.quit()


# 🚀 Ejecutar el script
if __name__ == "__main__":
    extraer_libros()
