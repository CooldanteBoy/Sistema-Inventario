import sqlite3
import hashlib
import datetime
from typing import List, Optional

from models import User, Product, Warehouse

DB_NAME = "InventarioBD_2.db"


class Database:
    def __init__(self, db_name: str = DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row

        self._create_user_table()
        self._ensure_default_users()
        self._ensure_audit_columns()

    # ------------------------------------------------------------------
    #  USUARIOS
    # ------------------------------------------------------------------

    def _create_user_table(self) -> None:
        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fecha_hora_ultimo_inicio TEXT,
                rol TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def _ensure_default_users(self) -> None:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) AS n FROM usuarios")
        row = c.fetchone()
        if row["n"] == 0:
            self.create_user("ADMIN", "admin23", "ADMIN")
            self.create_user("PRODUCTOS", "productos19", "PRODUCTOS")
            self.create_user("ALMACENES", "almacenes11", "ALMACENES")

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Encriptación sencilla MD5.
        """
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    def create_user(self, username: str, password: str, role: str) -> None:
        password_hash = self._hash_password(password)
        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO usuarios (nombre, password, rol)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role),
        )
        self.conn.commit()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:

        c = self.conn.cursor()
        username = username.strip()
        password_hash = self._hash_password(password)

        c.execute(
            """
            SELECT id, nombre, password, rol, fecha_hora_ultimo_inicio
            FROM usuarios
            WHERE nombre = ? AND password = ?
            """,
            (username, password_hash),
        )
        row = c.fetchone()

        if not row:
            # Usuario o contraseña incorrectos
            return None

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "UPDATE usuarios SET fecha_hora_ultimo_inicio=? WHERE id=?",
            (now_str, row["id"]),
        )
        self.conn.commit()

        return User(
            id=row["id"],
            username=row["nombre"],
            role=row["rol"],
            last_login=row["fecha_hora_ultimo_inicio"],
        )

    # ------------------------------------------------------------------
    #  COLUMNAS DE AUDITORÍA (PRODUCTOS Y ALMACENES)
    # ------------------------------------------------------------------

    def _ensure_audit_columns(self) -> None:
        c = self.conn.cursor()

        # ---------- PRODUCTOS ----------
        c.execute("PRAGMA table_info(productos)")
        cols_prod = [row[1].lower() for row in c.fetchall()]

        if "fecha_hora_creacion" not in cols_prod:
            c.execute("ALTER TABLE productos ADD COLUMN fecha_hora_creacion TEXT")
        if "fecha_hora_ultima_modificacion" not in cols_prod:
            c.execute("ALTER TABLE productos ADD COLUMN fecha_hora_ultima_modificacion TEXT")
        if "ultimo_usuario_en_modificar" not in cols_prod:
            c.execute("ALTER TABLE productos ADD COLUMN ultimo_usuario_en_modificar TEXT")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            """
            UPDATE productos
            SET fecha_hora_creacion = COALESCE(fecha_hora_creacion, ?)
            """,
            (now,),
        )

        # ---------- ALMACENES ----------
        c.execute("PRAGMA table_info(almacenes)")
        cols_alm = [row[1].lower() for row in c.fetchall()]

        if "fecha_hora_creacion" not in cols_alm:
            c.execute("ALTER TABLE almacenes ADD COLUMN fecha_hora_creacion TEXT")
        if "fecha_hora_ultima_modificacion" not in cols_alm:
            c.execute("ALTER TABLE almacenes ADD COLUMN fecha_hora_ultima_modificacion TEXT")
        if "ultimo_usuario_en_modificar" not in cols_alm:
            c.execute("ALTER TABLE almacenes ADD COLUMN ultimo_usuario_en_modificar TEXT")

        c.execute(
            """
            UPDATE almacenes
            SET fecha_hora_creacion = COALESCE(fecha_hora_creacion, ?)
            """,
            (now,),
        )

        self.conn.commit()

    # ------------------------------------------------------------------
    #  PRODUCTOS
    # ------------------------------------------------------------------

    def list_products(self) -> list[Product]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM productos ORDER BY id")
        rows = c.fetchall()

        products: List[Product] = []
        for r in rows:
            last_modified = None
            if "fecha_hora_ultima_modificacion" in r.keys():
                last_modified = r["fecha_hora_ultima_modificacion"]

            products.append(
                Product(
                    id=r["id"],
                    name=r["nombre"],
                    description=r["departamento"],
                    price=r["precio"],
                    stock=r["cantidad"],
                    last_modified=last_modified,
                )
            )
        return products

    def add_product(
            self,
            name: str,
            description: str,
            price: float,
            stock: int,
            username: str,
    ) -> None:
        c = self.conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            """
            INSERT INTO productos
            (nombre, precio, cantidad, departamento, almacen,
             fecha_hora_creacion, fecha_hora_ultima_modificacion, ultimo_usuario_en_modificar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, price, stock, description, 1, now, now, username),
        )
        self.conn.commit()

    def update_product(
            self,
            product_id: int,
            name: str,
            description: str,
            price: float,
            stock: int,
            username: str,
    ) -> None:
        c = self.conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            """
            UPDATE productos
            SET nombre = ?,
                precio = ?,
                cantidad = ?,
                departamento = ?,
                fecha_hora_ultima_modificacion = ?,
                ultimo_usuario_en_modificar = ?
            WHERE id = ?
            """,
            (name, price, stock, description, now, username, product_id),
        )
        self.conn.commit()

    def delete_product(self, product_id: int) -> None:
        c = self.conn.cursor()
        c.execute("DELETE FROM productos WHERE id = ?", (product_id,))
        self.conn.commit()

    def get_product_audit(self, product_id: int):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT fecha_hora_creacion,
                   fecha_hora_ultima_modificacion,
                   ultimo_usuario_en_modificar
            FROM productos
            WHERE id = ?
            """,
            (product_id,),
        )
        return c.fetchone()

    # ------------------------------------------------------------------
    #  ALMACENES
    # ------------------------------------------------------------------

    def list_warehouses(self) -> list[Warehouse]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM almacenes ORDER BY id")
        rows = c.fetchall()

        warehouses: List[Warehouse] = []
        for r in rows:
            last_modified = None
            if "fecha_hora_ultima_modificacion" in r.keys():
                last_modified = r["fecha_hora_ultima_modificacion"]

            warehouses.append(
                Warehouse(
                    id=r["id"],
                    name=r["nombre"],
                    last_modified=last_modified,
                )
            )
        return warehouses

    def add_warehouse(self, warehouse_id: int, name: str, username: str) -> None:

        c = self.conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
        """
        INSERT INTO almacenes
        (id, nombre, fecha_hora_creacion, fecha_hora_ultima_modificacion, ultimo_usuario_en_modificar)
        VALUES (?, ?, ?, ?, ?)
        """,
        (warehouse_id, name, now, now, username),
        )
        self.conn.commit()


    def update_warehouse(self, warehouse_id: int, name: str, username: str) -> None:
        c = self.conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
        """
        UPDATE almacenes
        SET nombre = ?,
            fecha_hora_ultima_modificacion = ?,
            ultimo_usuario_en_modificar = ?
        WHERE id = ?
        """,
        (name, now, username, warehouse_id),
        )
        self.conn.commit()

    def delete_warehouse(self, warehouse_id: int) -> None:
        c = self.conn.cursor()
        c.execute("DELETE FROM almacenes WHERE id = ?", (warehouse_id,))
        self.conn.commit()

    def get_warehouse_audit(self, warehouse_id: int):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT fecha_hora_creacion,
                   fecha_hora_ultima_modificacion,
                   ultimo_usuario_en_modificar
            FROM almacenes
            WHERE id = ?
            """,
            (warehouse_id,),
        )
        return c.fetchone()