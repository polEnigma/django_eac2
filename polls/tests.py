from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Crear administrador  a la base de dades proves
        User.objects.create_superuser(
            "isard",
            "isard@isardvdi.com",
            "pirineus"
        )

        options = Options()
        options.add_argument("-headless")

        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_crear_encuesta(self):

        # 1. Abrir el administrador de Django
        self.selenium.get(
            self.live_server_url + "/admin/"
        )

        # 2. Iniciar sesion
        self.selenium.find_element(
            By.NAME, "username"
        ).send_keys("isard")

        self.selenium.find_element(
            By.NAME, "password"
        ).send_keys("pirineus")

        self.selenium.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        # 3. Comprobar acceso al administrador
        self.assertIn(
            "Site administration",
            self.selenium.page_source
        )

        # 4. Acceder a crear una pregunta
        self.selenium.get(
            self.live_server_url + "/admin/polls/question/add/"
        )

        pregunta = "Cual es tu lenguaje favorito?"

        self.selenium.find_element(
            By.NAME, "question_text"
        ).send_keys(pregunta)

        # 5. Introducir fecha y hora
        ahora = timezone.localtime(timezone.now())

        self.selenium.find_element(
            By.NAME, "pub_date_0"
        ).send_keys(ahora.strftime("%Y-%m-%d"))

        self.selenium.find_element(
            By.NAME, "pub_date_1"
        ).send_keys(ahora.strftime("%H:%M:%S"))

        # 6. Crear tres respuestas
        respuestas = ["Python", "Java", "JavaScript"]

        for i, respuesta in enumerate(respuestas):
            self.selenium.find_element(
                By.NAME,
                f"choice_set-{i}-choice_text"
            ).send_keys(respuesta)

        # 7. Guardar desde el navegador
        self.selenium.find_element(
            By.NAME, "_save"
        ).click()

        # 8. Comprobar que aparece la pregunta
        enlace = self.selenium.find_element(
            By.LINK_TEXT, pregunta
        )

        self.assertTrue(enlace.is_displayed())

        # 9. Abrir la pregunta guardada
        enlace.click()

        # 10. Verificar las tres respuestas
        for i, respuesta in enumerate(respuestas):
            campo = self.selenium.find_element(
                By.NAME,
                f"choice_set-{i}-choice_text"
            )

            self.assertEqual(
                campo.get_attribute("value"),
                respuesta
            )
