"""Модуль виртуальной файловой системы (VFS)."""


import base64
import json
import os


class VFSError(Exception):
    """Ошибка при загрузке или работе с VFS."""


class VFS:
    """Виртуальная файловая система в памяти."""

    def __init__(self, name, root):
        self.name = name
        self.root = root

    @classmethod
    def load(cls, path):
        """Загружает VFS из JSON-файла в память."""
        if not os.path.exists(path):
            raise VFSError(f"Файл не найден: {path}")

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise VFSError(f"Неверный формат JSON: {exc}") from exc
        except OSError as exc:
            raise VFSError(f"Ошибка чтения файла: {exc}") from exc

        if not isinstance(data, dict):
            raise VFSError("Неверный формат: корневой элемент должен быть объектом")
        if "name" not in data or "root" not in data:
            raise VFSError("Неверный формат: отсутствует 'name' или 'root'")

        # Рекурсивно расшифровываем бинарные данные (base64)
        cls._decode_node(data["root"])

        return cls(data["name"], data["root"])

    @classmethod
    def _decode_node(cls, node):
        """Рекурсивно проходит по дереву и расшифровывает base64."""
        if node.get("encoding") == "base64":
            raw = node.get("content", "")
            try:
                decoded = base64.b64decode(raw)
            except Exception as exc:
                raise VFSError(f"Ошибка base64 в файле: {exc}") from exc

            try:
                node["content"] = decoded.decode("utf-8")
            except UnicodeDecodeError:
                node["content"] = decoded

        # Если есть вложенные папки/файлы - идем вглубь
        for child in node.get("children", {}).values():
            cls._decode_node(child)