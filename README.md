# Sistema de Inventario – Python + Tkinter + SQLite

Proyecto desarrollado por Dante Durand Morales como solución eficiente y sencilla para la administración de productos y almacenes dentro de una empresa.
El sistema permite registrar, editar, eliminar y buscar productos, así como gestionar almacenes con auditoría de cambios y control de accesos por usuario.

# 📌 Tabla de Contenidos
- [Descripción general](#descripción-general)
- [Características principales](#características-principales)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Roles y autenticación](#roles-y-autenticación)
- [Interfaz gráfica](#interfaz-gráfica)
- [Desafíos y soluciones](#desafíos-y-soluciones)
- [Cómo ejecutar el proyecto](#cómo-ejecutar-el-proyecto)
- [Capturas del sistema](#capturas-del-sistema-opcional)
- [Conclusión](#conclusión)


# Descripción general

Muchas empresas pequeñas siguen administrando inventarios manualmente o usando herramientas básicas como Excel. Estos métodos provocan:

- Falta de información en tiempo real

- Dificultad para encontrar productos

- Errores humanos frecuentes

- Tiempos largos al generar reportes

Este proyecto implementa un sistema de inventario digital creado con:

- Python 3

- Tkinter (interfaz gráfica)

- SQLite (base de datos local)

- Pillow (manejo de imágenes)

- PyInstaller (para generar ejecutables)


# ⭐ Características principales

### ✔ Inicio de sesión seguro con roles

Usuario: ADMIN

Usuario: PRODUCTOS

Usuario: ALMACENES

Cada uno tiene diferentes permisos sobre el sistema.

### ✔ Gestión completa de productos

- Registrar productos

- Editarlos

- Eliminarlos

- Fecha de creación

- Última modificación

- Usuario que modificó

### ✔ Búsquedas avanzadas

#### Filtros por:

- ID

- Nombre

- Descripción

- Precio mínimo / máximo

- Existencias mínimas / máximas

### ✔ Gestión de almacenes

CRUD completo con historial de modificaciones igual que los productos.

### ✔ Navegación estable

Una ventana principal con botones fijos:

#### Inicio | Productos | Almacenes | Cerrar sesión


# 🏗 Arquitectura del proyecto

El sistema está dividido en módulos, mejorando la organización y mantenibilidad del código:


#### main.py:	
Punto de entrada de la aplicación. Crea la conexión y lanza la ventana de login.

#### database.py
Manejo completo de SQLite: usuarios, productos, almacenes y auditoría.

#### models.py
Contiene las clases User, Product, Warehouse usando dataclasses.
#### ui.py
Toda la interfaz gráfica: login, vistas, diálogos y navegación.


# 🗄 Base de datos

Las tablas principales son:

- ## Usuarios

Contiene:

- nombre

- contraseña (hash MD5)

- rol

- último inicio de sesión

- ## Productos


- id

- nombre

- departamento

- precio

- existencias

- auditoría (creación, última modificación, quién modificó)

## Almacenes


- id

- nombre

- auditoría completa


# 🔐 Roles y autenticación

La función authenticate_user() valida usuario/contraseña y registra el último inicio de sesión.
Cada vista habilita o deshabilita botones según el rol:

ADMIN → acceso total

PRODUCTOS → CRUD productos

ALMACENES → CRUD almacenes

# 🖥 Interfaz gráfica

La UI está construida con Tkinter e incluye:

- Login estilizado

- Ventana principal con frame fijo

- HomeView

- ProductsView

- WarehousesView

El uso de Treeview es para mostrar datos en tablas

# 🧩 Desafíos y soluciones
## 1. Lenguaje del proyecto

Reto: Código sencillo y rápido para desarrollar.

Solución: Se eligió Python en lugar de Java por su simplicidad y menor cantidad de boilerplate.

## 2. Filtros avanzados de búsqueda

Reto: Permitir buscar por rango de precios y existencias sin complicaciones.

Solución:
Se añadieron campos min/max y un botón Aplicar filtros, implementado desde:

ProductSearchDialog o WarehouseSearchDialog
que regresan los filtros en self.result.

## 3. Navegación entre ventanas

Reto: Los botones desaparecían al abrir Productos o Almacenes.

Solución:
Se rediseñó la arquitectura:

Ventana principal (MainWindow)

Frame inferior fijo con botones globales,
se cambia solo el contenido central usando _switch_view()
así los botones nunca se destruyen.

# ▶ Cómo ejecutar el proyecto
## Requerimientos
Python 3.10+
Pillow
tkinter (incluido en Python)

## Instalar dependencias
pip install pillow

Ejecutar
python main.py

## Usuarios por defecto

ADMIN / admin23

PRODUCTOS / productos19

ALMACENES / almacenes11

# 📷 Capturas del sistema
![Inicio de Sesion](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/Inicio%20de%20Sesion.png
)

![Home View](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/HomeView.png)

![Productos View](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/ProductosView.png)

![Agregar Productos](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/AgregarProducto.png)

![Busqueda Productos](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/BusquedaProducto.png)

![Almacenes View](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/WarehouseView.png)

![Agregar Almacen](https://github.com/CooldanteBoy/Sistema-Inventario/raw/master/imagenes/AgregarAlmacen.png)

# 🏁 Conclusión

Este sistema de inventario permite:

- Reducir errores humanos

- Consultar información en tiempo real

- Controlar existencias con mayor precisión

- Agilizar la toma de decisiones

- Mantener un registro de auditoría para mayor control

En resumen, ofrece una herramienta eficiente, clara y confiable para gestionar inventarios dentro de una empresa.