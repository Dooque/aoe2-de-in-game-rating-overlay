# Age of Empires II DE - In Game Rating Overlay

[Español](./README.es.md) | [English](./README.md)

## Descargar

Puedes descargar la última versión desde [aquí](https://github.com/Dooque/aoe2-de-in-game-rating-overlay/archive/refs/tags/v0.1.0.zip).

## Introducción

Es una ventana que muestra por encima de todo en la pantalla el ELO 1vs1 RM y el ELO TG RM para todos los jugadores en una partida multijugador.

Actualmente solo funciona para partidas de "Mapa Aleatorio".

Puedes mover el texto a cualquier posición en la pantalla. El programa recordará la posición de la ventana en la pantalla para la próxima vez que lo abras.

The 1v1 ELO is shown between *[ ]* and the TG ELO is shown between *( )*.
El ELO 1vs se muestre entre *[ ]* y el ELO TG se muestra entre *( )*.

![](./res/picture1.png)
![](./res/picture2.png)
![](./res/picture3.png)
![](./res/picture4.png)

Además es posible minimizar la ventana. Haciendo clic derecho sobre la ventana y luego clic en "Minimize".

La posición de la ventana minimizada es independiente de la ventana maximizada, así por ejemplo, entre un juego y otro puedes poner la ventana minimizada en una posición donde no interfiera con los menúes del juego.

![](./res/picture6.png)
![](./res/picture5.png)
![](./res/picture7.png)

## Instalación & Configuración

El programa no requiere instalación. Solo hay que extraer el archivo ZIP, configurar tu ID de perfil, instalar la fuente y ejecutar el archivo `aoe2de-mp-ratings.exe`

La fuente se instala haciendo doble clic en el archivo `LiberationMono-Bold.ttf`, y luego haciendo clic en el botón `Instalar`. Una vez instalada la ventana de la fuente se puede cerrar.

La única configuración que se necesita es escribir tu ID del perfil de [AoE2.net](https://aoe2.net) en el archivo `AOE2NET_PROFILE_ID.txt`.

### Cómo cierro el programa?

Clic derecho en la ventana y luego clic en `Exit`.

### Cómo obtengo mi ID de perfil de AoE2.net?

Dirígete a https://aoe2.net/.

Clic en "Marcadores" y elegimos "Mapa Aleatorio (RM)":

![](./res/picture8.png)

En la sección para buscar ingresamos nuestro nombre de perfil de Steam. Una vez que te veas a ti mismo en la tabla hace clic sobre tu nombre:

> NOTA: Si no figuras en la lista es porque no has jugado al menos 10 juegos puntuados (ranked). Es necesario haber jugado al menos 10 partidas en la cola con clasificación para tener un ID de perfil de AoE2.net.

![](./res/picture9.png)

Clic en el botón de "perfil" que se encuentra en la parte inferior derecha de la ventana:

![](./res/picture10.png)

Luego podrás ver tu ID de perfil en la URL:

![](./res/picture11.png)

Copia y pega el número en el archivo `AOE2NET_PROFILE_ID.txt`.

Y eso es todo, ya puede ejecutar `aoe2de-mp-ratings.exe`.

## Próximamente?

1. Poder cambiar el color, fuente y tamaño del texto desde un archivo de configuración.
2. Poder seleccionar un fondo de color sólido desde un archivo de configuración.
4. Mostrar el texto con el modo de colores aliado/enemigo "azul/amarillo/rojo".
6. Poder modificar el tiempo de actualización desde un archivo de configuración.

## HISTORIAL DE CAMBIOS

### v0.2.0

* Se cambió el tamaño de fuente de 11 a 9.
* Se cambió el tipo de fuente de Britannic Bold a Liberation Mono Bold.
* Archivo de fuente agregado para ser instalado.
* Añadido banner de carga.
* Añadido menú para cerrar el programa.
* Menú agregado para minimizar / maximizar la ventana.
* Menú agregado para actualizar la información del juego.
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
