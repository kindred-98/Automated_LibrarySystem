
# ---------------- FIXTURE ----------------

import pytest
from src.services.biblioteca import Biblioteca
from src.models.libro import Libro


@pytest.fixture
def biblioteca(tmp_path):
    archivo_temporal = tmp_path / "libros_test.json"
    return Biblioteca(archivo=str(archivo_temporal))

# ---------------- TESTS BÁSICOS ----------------

def test_agregar_libro_y_listar(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)

    libros = biblioteca.listar_libros()
    assert len(libros) == 1
    assert libros[0].titulo == "1984"


def test_no_permitir_libro_duplicado(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)

    with pytest.raises(ValueError):
        biblioteca.agregar_libro(libro)


# ---------------- PRÉSTAMO / DEVOLUCIÓN ----------------

def test_prestar_libro_exitoso(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)

    ok, _ = biblioteca.prestar_libro("1")
    assert ok is True
    assert libro.disponible is False


def test_prestar_libro_ya_prestado(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)
    biblioteca.prestar_libro("1")

    ok, _ = biblioteca.prestar_libro("1")
    assert ok is False


def test_devolver_libro_exitoso(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)
    biblioteca.prestar_libro("1")

    ok, _ = biblioteca.devolver_libro("1")
    assert ok is True
    assert libro.disponible is True


# ---------------- BÚSQUEDAS ----------------

def test_buscar_libro_por_id(biblioteca):
    libro = Libro(1, "1984", "George Orwell")
    biblioteca.agregar_libro(libro)

    resultado = biblioteca.buscar_por_titulo("1984")
    assert resultado is not None
    assert resultado.autor == "George Orwell"


def test_buscar_libro_inexistente(biblioteca):
    resultado = biblioteca.buscar_por_titulo("No existe")
    assert resultado is None


def test_buscar_libro_por_autor(biblioteca):
    libro1 = Libro(1, "1984", "George Orwell")
    libro2 = Libro(2, "Animal Farm", "George Orwell")
    libro3 = Libro(3, "Brave New World", "Aldous Huxley")

    biblioteca.agregar_libro(libro1)
    biblioteca.agregar_libro(libro2)
    biblioteca.agregar_libro(libro3)

    resultados = biblioteca.buscar_por_autor("George Orwell")
    assert len(resultados) == 2