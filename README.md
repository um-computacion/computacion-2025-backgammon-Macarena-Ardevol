# Backgammon Computación 2025

Este proyecto implementa el juego **Backgammon** en Python, siguiendo las consignas de la materia Computación 2025.  
El desarrollo contempla tanto una interfaz de línea de comandos (CLI) como una interfaz gráfica basada en **Pygame**.

## Estructura inicial del proyecto

/backgammon/
├── core: lógica del juego (clases principales)
├── cli: interfaz de línea de comandos
├── pygame_ui: interfaz gráfica con Pygame
├── assets: imágenes, sonidos
├── requirements.txt

/tests/ (pruebas unitarias)
├── test errores (pruebas para posibles errores)
├── test válidos (pruebas para casos válidos)

## Guía para correr los tests: 

Este proyecto incluye un conjunto de tests automatizados, divididos en dos grupos:
	•	Tests válidos: verifican que el código funcione correctamente frente a entradas esperadas.
	•	Tests de errores: verifican que el código maneje adecuadamente entradas inválidas o situaciones límite.

### Ejecución de todos los tests:

Para ejecutar todos los tests de una sola vez, situarse en la raíz del proyecto y correr:

*python -m unittest discover*

Este comando utiliza el módulo estándar unittest de Python y busca automáticamente todos los archivos cuyo nombre comience con test_ dentro de la carpeta tests/.

### Ejecución de un archivo de tests específico

Si se desea ejecutar únicamente los tests de un archivo en particular, por ejemplo los de casos válidos:

*python -m unittest tests/test_validos/test_funciones.py*

### Interpretación de resultados

Al finalizar la ejecución, unittest muestra un resumen indicando:
	•	El número de tests ejecutados.
	•	El tiempo empleado.
	•	El estado general: OK, FAILED (fallos) o ERROR (excepciones).

Ejemplos: 

### Todos los tests pasan:

..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK

•	Cada . indica un test exitoso.
	•	OK confirma que no hubo problemas.

### Un test falla:

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

	•	La F indica un fallo.
	•	Se detalla qué test falló, en qué archivo y línea.
	•	El resumen final indica cuántos fallos hubo.

### Error en la ejecución:

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
	•	La E muestra un error en la ejecución (por ejemplo, una excepción no controlada).
	•	El detalle muestra el tipo de error y dónde ocurrió.