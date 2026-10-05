import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog

try:
    import requests
except ImportError:
    requests = None

from src.services.biblioteca import Biblioteca
from src.models.libro import Libro

PROMPT_ID_LIBRO = "ID del libro:"
PROMPT_TITULO = "Título:"


class BibliotecaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Biblioteca Talento Solutions")

        self.biblioteca = Biblioteca()

        self.lista = tk.Listbox(root, width=60)
        self.lista.pack(pady=10)

        self._crear_botones()
        self.actualizar_lista()

    def _crear_botones(self):
        botones = [
            ("Agregar Libro", self.agregar),
            ("Prestar Libro", self.prestar),
            ("Devolver Libro", self.devolver),
            ("Buscar Local", self.buscar_local),
            ("Buscar Open Library", self.buscar_publico),
            ("Actualizar", self.actualizar_lista),
        ]

        for texto, comando in botones:
            tk.Button(self.root, text=texto, command=comando).pack(fill="x")

    def actualizar_lista(self):
        self.lista.delete(0, tk.END)
        for libro in self.biblioteca.listar_libros():
            estado = "Disponible" if libro.disponible else "Prestado"
            self.lista.insert(
                tk.END,
                f"{libro.id} - {libro.titulo} - {libro.autor} ({estado})"
            )

    def agregar(self):
        id_libro = simpledialog.askstring("ID", PROMPT_ID_LIBRO)
        titulo = simpledialog.askstring("Título", PROMPT_TITULO)
        autor = simpledialog.askstring("Autor", "Autor:")

        if not (id_libro and titulo and autor):
            return

        try:
            libro = Libro(id_libro, titulo, autor)
            self.biblioteca.agregar_libro(libro)
            self.actualizar_lista()
            messagebox.showinfo("Éxito", "Libro agregado.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def prestar(self):
        id_libro = simpledialog.askstring("Prestar", PROMPT_ID_LIBRO)
        _, msg = self.biblioteca.prestar_libro(id_libro)
        messagebox.showinfo("Resultado", msg)
        self.actualizar_lista()

    def devolver(self):
        id_libro = simpledialog.askstring("Devolver", PROMPT_ID_LIBRO)
        _, msg = self.biblioteca.devolver_libro(id_libro)
        messagebox.showinfo("Resultado", msg)
        self.actualizar_lista()

    def buscar_local(self):
        titulo = simpledialog.askstring("Buscar", PROMPT_TITULO)
        libro = self.biblioteca.buscar_por_titulo(titulo)
        if libro:
            messagebox.showinfo("Encontrado", str(libro))
        else:
            messagebox.showwarning("No encontrado", "No existe.")

    def buscar_publico(self):
        titulo = simpledialog.askstring("Buscar OpenLibrary", PROMPT_TITULO)
        if not titulo:
            return

        if requests is None:
            messagebox.showerror(
                "Dependencia no instalada",
                "Instale requests para buscar en Open Library:\n" \
                "pip install requests"
            )
            return

        try:
            r = requests.get(
                f"https://openlibrary.org/search.json?title={titulo}"
            )
            r.raise_for_status()
        except Exception:
            messagebox.showerror("Error", "No se pudo consultar Open Library.")
            return

        docs = r.json().get("docs", [])[:5]

        if not docs:
            messagebox.showinfo("Resultados", "Sin resultados.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Resultados Open Library")

        tk.Label(ventana, text="Resultados de la búsqueda:", font=("Arial", 12, "bold")).pack(pady=5)

        for d in docs:
            titulo = d.get("title", "Sin título")
            autores = ", ".join(d.get("author_name", ["Desconocido"]))
            key = d.get("key")

            url = f"https://openlibrary.org{key}" if key else None

            texto = f"{titulo} - {autores}"

            label = tk.Label(ventana, text=texto, fg="blue", cursor="hand2")
            label.pack(anchor="w", padx=10)

            if url:
                label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))
