# 🚀 Flask API Boilerplate (Backend Único)

Una estructura base limpia, moderna y robusta para construir APIs REST utilizando **Python y Flask**. Este boilerplate ha sido diseñado específicamente de forma independiente para facilitar el aprendizaje y el despliegue rápido de servicios backend sin mezclar lógica de frontend.

---

## 🛠️ Tecnologías y Stack

![Python](https://img.shields.io/badge/python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/flask-3.0-white?style=for-the-badge&logo=flask&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Pipenv](https://img.shields.io/badge/pipenv-6b578c?style=for-the-badge&logo=python&logoColor=white)

---

## ⚙️ Instalación y Configuración Paso a Paso

> 💡 **Nota para principiantes:** Si trabajas en GitHub Codespaces o Gitpod, el entorno ya incluye Python y Postgres. Si estás trabajando en local, asegúrate de tener instalado Python 3.10, Pipenv y tu motor de base de datos preferido.

1. **Instala las dependencias del proyecto:**

   ```bash
   pipenv install

   ```

2. Crea tu archivo de configuración local (.env):

Bash
cp .env.example .env

3. Instala tu motor de base de datos y crea tu base de datos, dependiendo de tu base de datos, debes crear una variable DATABASE_URL con uno de los valores posibles, asegúrate de reemplazar los valores con la información de tu base de datos:

| Motor    | DATABASE_URL                                        |
| -------- | --------------------------------------------------- |
| SQLite   | sqlite:////test.db                                  |
| MySQL    | mysql://username:password@localhost:port/example    |
| Postgres | postgres://username:password@localhost:5432/example |

4. Detectar cambios en los modelos (Generar archivo de migración):
   Bash
   pipenv run flask db migrate -m "Initial migration"

5. Aplicar los cambios (Crear las tablas en la base de datos):
   Bash
   pipenv run flask db upgrade

🔄 Comandos Útiles y Datos de Prueba
Deshacer la última migración
Si te has equivocado en un modelo y necesitas revertir el último cambio en las tablas:
Para fallos en migraciones con ramas divergentes:

    pipenv run flask db stamp heads

    Bash
    pipenv run flask db downgrade

🔐 Seguridad y Buenas Prácticas

    Variables Ocultas: El archivo .env está en el .gitignore. Nunca lo subas a GitHub. Para producción (en Render, Heroku, etc.), introduce estas variables directamente en el panel de control de tu proveedor.

    Código Organizado: Toda la lógica de la API, rutas y modelos están completamente aislados dentro de la carpeta src/api/, listos para conectar con cualquier frontend independiente (React, Vue, Vanilla JS, etc.).

    Boilerplate abierto y optimizado para impulsar el desarrollo backend en la comunidad.
