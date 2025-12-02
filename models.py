from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    role: str
    last_login: Optional[str]


@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int
    last_modified: Optional[str]


@dataclass
class Warehouse:
    id: int
    name: str
    last_modified: Optional[str]
