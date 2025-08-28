# JUSTIFICACION - Backgammon Computación 2025

### Diseño general
El proyecto está diseñado con separación clara entre lógica central (core), interfaz de línea de comandos (CLI) e interfaz gráfica con Pygame (pygame_ui).  
Este diseño facilita mantener las reglas del juego independientes de la presentación.

### Clases elegidas
- **BackgammonGame**: Coordina el flujo del juego (gestiona turnos, condiciones de victoria, etc).
- **Board**: Representa el tablero con sus 24 puntos.
- **Player**: Representa a cada jugador (nombre, fichas).
- **Dice**: Lógica de tiradas (dos dados de seis caras).
- **Checker**: Representa cada ficha del tablero.
- **CLI**: Interfaz de texto.
- **PygameUI**: Interfaz gráfica.

### Atributos
Por completar 

### Excepciones y manejo de errores
Por completar

### Estrategia de testing
Se utilizarán tests unitarios con unittest, alcanzando al menos 90% de cobertura en core.  
Se incluirán tests de “casos errores” y “casos válidos”.

### Principios SOLID
Por completar

### Diagramas UML
Por completar