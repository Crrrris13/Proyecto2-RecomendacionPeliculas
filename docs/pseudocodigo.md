# Pseudocódigo del Sistema de Recomendación

## Función principal


```
FUNCIÓN recomendar_peliculas(usuario_id):

// Paso 1: Obtener nodo usuario del grafo
usuario ← buscar_usuario(usuario_id)
peliculas_vistas ← obtener_peliculas_vistas(usuario)

recomendaciones ← diccionario (pelicula → puntaje)

// Paso 2: Filtrado colaborativo (usuarios similares en el grafo)
usuarios_similares ← buscar_usuarios_similares(usuario)

PARA cada u EN usuarios_similares HACER:
    peliculas_u ← obtener_peliculas_gustadas(u)

    PARA cada pelicula EN peliculas_u HACER:
        SI pelicula NO está en peliculas_vistas ENTONCES:
            recomendaciones[pelicula] += 1
        FIN SI
    FIN PARA
FIN PARA

// Paso 3: Filtrado por contenido (recorriendo relaciones del grafo)
PARA cada pelicula_vista EN peliculas_vistas HACER:

    generos ← obtener_generos(pelicula_vista)
    actores ← obtener_actores(pelicula_vista)
    director ← obtener_director(pelicula_vista)

    peliculas_similares ← buscar_por_relaciones(generos, actores, director)

    PARA cada pelicula EN peliculas_similares HACER:
        SI pelicula NO está en peliculas_vistas ENTONCES:
            recomendaciones[pelicula] += 2
        FIN SI
    FIN PARA

    // Relaciones directas SIMILAR_A
    peliculas_relacionadas ← obtener_similares(pelicula_vista)

    PARA cada pelicula EN peliculas_relacionadas HACER:
        SI pelicula NO está en peliculas_vistas ENTONCES:
            recomendaciones[pelicula] += 3
        FIN SI
    FIN PARA

FIN PARA

// Paso 4: Ordenar por relevancia
lista_recomendaciones ← ordenar_por_puntaje(recomendaciones)

// Paso 5: Seleccionar top N
RETORNAR primeros 10 elementos de lista_recomendaciones

```

## Fin función principal