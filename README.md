# Backgammon — Computación 2025
### Macarena Ardevol

Implementación del juego **Backgammon** en Python para la cátedra de Computación 2025.  
El proyecto prioriza **POO + SOLID**, pruebas automatizadas y mejora continua. Incluye una **CLI** y (próximamente) una interfaz con **Pygame**.


## Descripción breve
- **Core** del juego (tablero, jugadores, dados, turnos) con encapsulamiento y API mínima.
- **CLI** para operaciones básicas (mostrar tirada y pips), con soporte opcional de `--setup` y `--roll a,b`.
- Documentación y tests que evolucionan gradualmente a lo largo de los sprints.


## Estructura del proyecto

- README.md — presentación, instalación, uso (este archivo)
- CHANGELOG.md — historial de cambios
- JUSTIFICACION.md — decisiones de diseño, SOLID, testing
- prompts-desarrollo.md, prompts-testing.md, prompts-documentacion.md — registro de interacción con IA
- .github/workflows/ci.yml — integración continua (tests/cobertura en GitHub Actions)

backgammon/
  core/ — lógica del juego
      board.py — 24 puntos; num_points(), get_point()/set_point(), setup_initial(), count_total(color)
      dice.py — tiradas de 2 dados; is_double()
      player.py, checker.py — getters públicos
      game.py — jugadores y turnos; start_turn(roll), last_roll(), pips(), setup_board()

  cli/ — interfaz de línea de comandos
      app.py — main() con --setup y --roll a,b
      __main__.py — entrypoint para python -m backgammon.cli

pygame_ui/ — interfaz con Pygame (pendiente)
assets/ — recursos (imágenes, sonidos)
requirements.txt — dependencias

tests/
      test_validos/ — pruebas para casos válidos (p. ej., test_core.py)
      test_errores/ — pruebas de entradas inválidas/límites (p. ej., test_errores.py)


## Requisitos
- Python **3.10+**
- `pip`


## Instalación de dependencias
```
python -m pip install --upgrade pip
pip install -r backgammon/requirements.txt
```

## Ejecutrar en modo CLI 
**Inicializar el tablero estándar y usar una tirada fija:**
```
python -m backgammon.cli --setup --roll 3,4
```
Nota: --roll a,b acepta enteros del 1 al 6. Formatos inválidos o valores vacíos generan ValueError.

## Tirada automática (sin setup):
```
python -m backgammon.cli 
```


## Ejecutar en modo Pygame (pendiente)

Esta sección se completará cuando se integre la UI de Pygame.
Se documentarán requisitos específicos y el comando de ejecución correspondiente.


## ¿Cómo correr los tests? 

Este proyecto incluye un conjunto de tests automatizados, divididos en dos grupos:

  *Tests válidos:* verifican que el código funcione correctamente frente a entradas esperadas.
  *Tests de errores:* verifican que el código maneje adecuadamente entradas inválidas o situaciones límite.

**Ejecución de todos los tests**
Situarse en la raíz del proyecto y correr:
   ```
    python -m unittest discover
	```

Este comando utiliza el módulo estándar unittest de Python y busca automáticamente todos los archivos cuyo nombre comience con test_ dentro de la carpeta tests/.


### Ejecución de un archivo de tests específico

Por ejemplo, los de casos válidos:
         *python -m unittest tests/test_validos/test_funciones.py* 

**Interpretación de resultados**
#### Todos los tests pasan:
```
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```

- Cada . indica un test exitoso.
- OK confirma que no hubo problemas.

#### Un test falla:
```
.F
======================================================================
FAIL: test_conversion_decimal_a_romano (tests.test_validos.test_funciones.TestConversion)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/ruta/proyecto/tests/test_validos/test_funciones.py", line 10, in test_conversion_decimal_a_romano
    self.assertEqual(decimal_to_roman(10), "X")
AssertionError: 'V' != 'X'

----------------------------------------------------------------------
Ran 2 tests in 0.002s

FAILED (failures=1)
```

- La F indica un fallo.
- Se detalla qué test falló, en qué archivo y línea.
- El resumen final indica cuántos fallos hubo.

#### Error en la ejecución:
```
E
======================================================================
ERROR: test_conversion_cero (tests/test_errores/test_excepciones.TestConversionErrores)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/ruta/proyecto/tests/test_errores/test_excepciones.py", line 8, in test_conversion_cero
    decimal_to_roman(0)
  File "/ruta/proyecto/src/roman.py", line 5, in decimal_to_roman
    raise ValueError("Los números romanos no tienen representación para 0")
ValueError: Los números romanos no tienen representación para 0

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```


- La E muestra un error en la ejecución (por ejemplo, una excepción no controlada).
- El detalle muestra el tipo de error y dónde ocurrió.

### Convenciones

Atributos de instancia con formato self.__nombre__.
Docstrings en clases y métodos.
Cambios incrementales y trazables (máx. 3 commits/día contables).