# Age of Empires II DE - In Game Rating Overlay

[Español](./README.es.md) | [English](./README.md)

Únete a la discución en [Discord](https://discord.gg/5Ke9Fa5G5x)

## Descargar

Puedes descargar la última versión desde [aquí](https://github.com/Dooque/aoe2-de-in-game-rating-overlay/archive/refs/tags/v1.0.1.zip).

## Introducción

Este programa es una ventana que muestra por encima de todo en la pantalla el ELO 1vs1 RM y el ELO TG RM para todos los jugadores en una partida multijugador.

Actualmente solo funciona para partidas de "Mapa Aleatorio". En versiones futuras incluiremos "Combate Total" y "Guerras Imperiales".

Puedes mover el texto a cualquier posición en la pantalla. El programa recordará la posición de la ventana en la pantalla para la próxima vez que lo abras.

El ELO 1v1 se muestre entre *[ ]* y el ELO TG se muestra entre *( )*.

![](./res/image-1.png)
![](./res/image-2.png)

Se puede ver información extendida de cada jugador dejando el puntero del mouse encima del nombre de cadad jugador:

![](./res/image-3.png)

Puedes elegir entre perfiles de múltiples jugadores haciendo clic derecho sobre la ventana y seleccionando el nombre del jugador en el menú "Users".

![](./res/image-4.png)

Para poder hacer eso previemente necesitas agregar el nombre y el ID de Steam de cada jugador en el archivo de configuración `configuration.txt`:

```json
{
  "users": [
    {"name":"Dooque", "ID":76561198982469653, "current":1},
    {"name":"Mendieta", "ID":76561199099265930, "current":0},
    {"name":"MentaPeperina", "ID":76561199203185042, "current":0}
  ],
}
```

Además es posible minimizar la ventana haciendo clic derecho sobre la misma y luego en el menú "Minimize".

![](./res/image-5.png)
![](./res/image-6.png)

La posisicón de la ventana minimizada es independiente de la posición de la ventana principal de manera que, por ejemplo, entre partidas puedes colocarla en alguna posición que no interfiera con los menúes del juego.

Para maximizar la ventana hacer clic derecho y seleccionar "Maximize".

![](./res/image-7.png)

Hay más opciones en el menú, simplemente has clic derecho y échale un vistazo.

![](./res/image-8.png)

## Instalación & Configuración

El programa no requiere instalación. Solo hay que extraer el archivo ZIP, configurar tu [ID de perfil de Steam](https://steamcommunity.com/login/home/?goto=) en el archivo `configuration.txt`, y ejecutar el archivo `aoe2de-in-game-rating-overlay.exe`

En el archivo de configuración `configuration.txt` además puedes modificar el tipo y tamaño de la fuente, como así también el tiempo de actualización "refresh-time".

```json
{
  "users": [
    {"name":"Dooque", "ID":76561198982469653, "current":1},
    {"name":"Mendieta", "ID":76561199099265930, "current":0},
    {"name":"MentaPeperina", "ID":76561199203185042, "current":0}
  ],
  "font-type":"Arial",
  "font-size":10,
  "refresh-time":10,
  "debug":false
}
```

> NOTA: `refresh-time` está expresado en segundos.

### Cómo cierro el programa?

Clic derecho en la ventana y luego clic en `Exit`.

### Cómo obtengo mi ID de perfil de Steam?

Dirígete a https://steamcommunity.com/login/home/?goto= e inicia sesión.

![](./res/image-9.png)

Mira en la parte de arriba en la bara con la URL, allí encontrarás tu ID de perfil de Steam.

![](./res/image-10.png)

Copia y pega el número en el archvio de configuración y eso es todo, ahora ya puedes ejecutar el programa haciendo doble clic en el archivo `aoe2de-in-game-rating-overlay.exe`.

## Qué sigue?

1. Poder cambiar el color del texto desde un archivo de configuración.
2. Poder seleccionar un fondo de color sólido desde un archivo de configuración.
3. Mostrar el texto con el modo de colores aliado/enemigo "azul/amarillo/rojo".
4. Hacer que funcione para Guerras Imperiales.
5. Hacer que funcione para Combate Total.
6. Hacer que la aplicación recuende el jugador seleccionado.

## Peroblemas Conocidos

1. Luego de actualizaciones de los servidores o del juego la aplicación puede tener problemas para conectarse a los servidores. SOLUCIÓN: El problema parese desaparecer luego de alrededor de 24 horas.
2. Si hay un segundo monitor conectado a la PC, y la aplicación se muestra en ese monitor, y luego se desconecta el monitor, la aplicación se seguirá mostrando en la posición de ese monitor, por lo que no se podrá ver la aplicación. SOLUCIÓN: Eliminar el archivo `C:\Users\USER\aoe2de_in_game_rating_overlay-window_location.txt`.
3. La aplicación se queda en el estado "Waiting for server" si el jugador seleccionado no tiene nungún juego en el modo de multijugador.

## HISTORIAL DE CAMBIOS

### v1.0.1

* Se corrige error debido a cambios en la API de aoe2.net.

### v1.0.0

* Se reemplazó el uso del ID de perfil de aoe2.net por el ID de Steam.
* Ahora la aplicación puede manejar múltiples perfiles de jugadores.
* Ahora la aplicación consulta e informa de nuevas versiones disponibles.
* Los nombres de los jugadores son de tamaño fijo ahora, por lo que la ventana es más pequeña.
* Se modificó la información extendida de cada jugado para que sea más pequeña.
* Se corrigió un error con el botón "Refresh".
* Se corrigen errores relacionados a la infomarcion del mach, ya que algunas veces la informacion esta incompleta en terminos de los valores de equipo y color de cada jugador.
* Se corrige un error done la ventana principal se desfazaba algunos pixeles luego de un refresh.

### v0.2.1

* Se corrigió un error donde el programa se cerraba si el servidor no estaba disponible.
* Se corrigió un error donde la posición de las ventanas cambiaba cuando se pasaba de Minimizado a Maximizado.
* Se corrigió un problema donde al hace clic en "Refresh" los datos no se actualizaban si no había comenzado una nueva partida.

### v0.2.0

* Se cambió el tamaño de fuente de 11 a 9.
* Se cambió el tipo de fuente de Britannic Bold a Liberation Mono Bold.
* Archivo de fuente agregado para ser instalado.
* Añadido banner de carga.
* Añadido menú para cerrar el programa.
* Menú agregado para minimizar / maximizar la ventana.
* Menú agregado para actualizar la información del juego.
* Se agregó información extendida de cada jugador cuando se pasa el puntero del mouse sobre el nombre.
* Derechos de autor agregados.

### v0.1.0

* Se cambió el tamaño de fuente de 14 a 11.
* Se cambió el tipo de fuente de Arial a Britannic Bold.
* Añadido color de texto para cada jugador.
* La ventana recuerda la última posición en la pantalla.

### v0.0.1

* Se trae el último juego del ID de perfil de AoE2.net guardado en el archivo `AOE2NET_PROFILE_ID.txt`.
* Se buscan a todos los jugadores del último juego.
* Se obtiene la siguiente información de cada jugador:
   * Clasificación de mapa aleatorio 1v1.
   * Número de victorias en el mapa aleatorio 1v1.
   * Número de pérdidas en el mapa aleatorio 1v1.
   * Racha de mapa aleatorio 1v1.
   * Clasificación de juego de equipo de mapa aleatorio.
   * Número de victorias del juego de equipo de mapa aleatorio
   * Número de derrotas del juego de equipo de mapa aleatorio.
   * Racha de juegos aleatorios en equipo.
* Se muestra parte de la información en una ventana transparente de fuente de texto fija (Arial), tamaño (14) y color. (blanco).
* El programa busca un nuevo juego cada una cantidad fija de tiempo (10 segundos).

- - -

*Age of Empires II Definitive Edition © Microsoft Corporation. Age of Empires II DE - In Game Rating Overlay was created under [Microsoft's "Game Content Usage Rules"](https://www.xbox.com/en-US/developers/rules) using assets from Age of Empires II Definitive Edition, and it is not endorsed by or affiliated with Microsoft.*
