## Prompt para documentación de tests

(1)
Herramienta usada: IA - ChatGPT 
Prompt utilizado: "Dame ejemplos concretos de la salida que aparece por consola cuando un test corre de manera correcta, cuando un test falla y cuando hay error en la ejecución"

Respuesta IA: 

### Todos los test pasan: 
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK

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

La salida fue usada sin cambios. 

Archivo final que incorporó contenido generado por IA: 
- README.md 

----------------------------------------------------------------------------------------------------------
