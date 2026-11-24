Clima y ocupación hotelera en Francia (2019-2026)

Proyecto final del curso de Data Analytics. 
Autora: Lucia Bravo 


1. Descripción del proyecto

Vivo en Chamonix-Mont-Blanc (Haute-Savoie, Alpes franceses), una zona cuyo turismo depende mucho de la estación del año. Este proyecto parte de una pregunta:

¿Cómo se relacionan la temporada y el clima con la ocupación hotelera en Francia, y qué hace distinta a Haute-Savoie (Chamonix)?

Para responderla uní dos fuentes independientes (turismo hotelero del Insee y clima de Open-Meteo) para 101 departamentos franceses entre enero de 2019 y septiembre de 2026, y comparé Haute-Savoie con el resto del país.

2. Resultados principales
Hallazgo	Dato
La temporada marca la ocupación	Francia: 62,4 % en verano frente a 46,0 % en invierno
Haute-Savoie destaca en invierno	61,4 % frente a 46,0 % de Francia (+15,4 puntos)
En verano y entretiempo la diferencia es menor	+6,1 puntos en verano y +0,6 en entretiempo
Origen de los turistas	El 34 % de las noches en Haute-Savoie son de turistas extranjeros, igual que en Francia (34,3 %)
Clima y ocupación	Relación moderada con la temperatura (0,56) y las horas de sol (0,50); no implica causalidad

4. Fuentes de datos
#	Fuente	Contenido	Archivo en bruto
1	Insee – Fréquentation des hébergements touristiques (data.gouv.fr)	Noches, llegadas y ocupación de hoteles y alojamientos similares, por departamento, mes y origen del turista	data/raw/turismo/tour_freq_data.csv (193.107 filas, 23 columnas) y tour_freq_metadata.csv (diccionario de códigos)
2	Open-Meteo – Historical Weather API	Clima diario de 101 departamentos (2019-01-01 a 2026-09-30): temperaturas, precipitación, nieve, viento y sol	data/raw/clima/clima_XX.csv (101 archivos, 2.830 días cada uno)
Aux.	API Geo (geo.api.gouv.fr)	Coordenadas de cada departamento (media de los centros de sus comunas)	data/raw/departamentos_coordenadas.csv

5. Estructura del repositorio
proyecto-clima-turismo-francia/
├── data/
│   ├── raw/                      Datos en bruto (sin modificar)
│   │   ├── turismo/
│   │   ├── clima/
│   │   └── departamentos_coordenadas.csv
│   └── processed/                Datos transformados
│       ├── turismo_limpio.csv
│       ├── dataset_final_francia.csv      ← dataset final (55.779 filas, 29 columnas)
│       └── resumen_*.csv                  ← tablas para el dashboard
├── scripts/                      Código en Python (ejecutar en orden)
├── exploracion/                  Primer análisis, solo de Chamonix
├── dashboard/                    Capturas y enlace del dashboard
├── report/                       Informe del análisis
└── README.md
6. Pasos seguidos
Paso 0 – Exploración inicial (Chamonix)

Empecé con un solo punto (Chamonix) y datos de Haute-Savoie: 48 meses de 2022 a 2025. Sirvió para aprender el flujo de trabajo y plantear la pregunta, pero no cumplía el tamaño mínimo del proyecto (50.000 filas y 20 columnas), así que amplié el alcance a toda Francia. Los scripts están en exploracion/.

  Paso 1 – Coordenadas de los departamentos (01_coordenadas.py, 01b_coordenadas_reintento.py)

Se consultó la API Geo para obtener las comunas de cada departamento y se calculó la media de sus coordenadas. Algunas peticiones fallaron por cortes de conexión y se reintentaron con el segundo script. Resultado: 101 departamentos con latitud y longitud.

  Paso 2 – Descarga del clima (02_descargar_clima.py)

Se descargaron 8 variables diarias por departamento desde Open-Meteo: temperatura media, máxima y mínima, precipitación, lluvia, nieve, viento máximo y duración del sol. La API gratuita limita las peticiones (por minuto, hora y día), así que el script espera cuando toca y se puede reanudar: no vuelve a descargar los departamentos que ya tiene. Resultado: 101 archivos, 285.830 filas de clima diario.

  Paso 3 – Limpieza del turismo (03_limpiar_turismo.py)
Se filtraron los datos mensuales a nivel de departamento entre 2019-01 y 2026-09: de 193.107 a 63.891 filas.
Se eliminaron 12 columnas que tenían un único valor y no aportaban información.
Se creó valor_real = valor original × 10^(factor de escala), porque algunas cifras vienen en miles.
Se identificó que 8.112 valores estaban ausentes (estados O y Q según el metadata).

  Paso 4 – Unión de los datasets (04_unir_datasets.py)
El clima diario se agregó por mes y departamento (medias, totales, máximos y recuentos de días).
Se eliminaron las 8.112 filas de turismo sin dato: quedan 55.779 filas.
Se unieron turismo, coordenadas y clima por departamento y mes (unión por la izquierda, para no perder filas).
Se crearon las columnas derivadas anio, mes_num y temporada.
Controles: 0 duplicados, 0 nulos y 0 filas sin clima. Haute-Savoie en enero de 2022 coincide con mi primer análisis independiente (ocupación del 50,0 %).

  Paso 5 – Análisis (05_analisis.py)
Validación del dataset, tablas resumen para el dashboard (resumen_*.csv) y correlaciones entre el clima y la ocupación.

  Paso 6 – Dashboard (Google Sheets)
Se importaron las tablas resumen a Google Sheets y se construyó un dashboard con tres indicadores y cinco gráficos. Las conclusiones y limitaciones están en una pestaña aparte.

6. Dataset final
data/processed/dataset_final_francia.csv · 55.779 filas × 29 columnas · 101 departamentos · 2019-2026

Columna 	                    Descripción
GEO     	                    Código del departamento
departamento	                Nombre del departamento
lat, lon	                    Coordenadas usadas para el clima (media de sus comunas)
TIME_PERIOD	                  Mes (AAAA-MM)
anio, mes_num	                Año y número de mes
temporada	Invierno           (dic-mar), Verano (jun-sep) o Entretiempo (resto)
TOUR_RESID	                Origen del turista: 250 Francia · 1_X_250 Extranjero · 276 Alemania · 380 Italia · 56 Bélgica · 19 Américas · _T Total
TOUR_MEASURE	              Medida: NIGHT_SPENT (noches), ARR (llegadas), PLACE_OCCUPANCY_RATE (% de ocupación), PLACE_AVAIL (unidades ofrecidas)
UNIT_MEASURE	              Unidad: NR (número) o PT (porcentaje)
UNIT_MULT, DECIMALS	        Factor de escala (potencia de 10) y decimales de la cifra original
OBS_VALUE	                  Valor original del Insee
valor_real	                OBS_VALUE × 10^UNIT_MULT (valor que se usa en el análisis)
OBS_STATUS	                Estado del dato: A normal, P provisional, R revisado
OBS_STATUS_FR, CONF_STATUS	Otras marcas de estado y confidencialidad del Insee
temp_media,                 Temperaturas medias del mes (°C)
temp_max_media, 
temp_min_media	
precip_total,               Precipitación total y lluvia total del mes (mm)
lluvia_total	
nieve_total	                Nieve total del mes (cm, según el modelo)
viento_max	                Máxima del viento diario máximo (km/h)
horas_sol	                   Horas de sol del mes
dias_helada,               Días con mínima < 0 °C, con ≥ 1 mm de precipitación y con nieve
dias_lluvia, 
dias_nieve	

Cómo usar el dataset sin contar dos veces: los orígenes se solapan (_T incluye a todos y 1_X_250 incluye a Alemania, Italia, Bélgica y Américas). Para totales, filtra TOUR_RESID == "_T". Tampoco se mezclan medidas distintas: noches y llegadas son recuentos y la ocupación es un porcentaje, que solo existe para el total.

7. Análisis y resultados

Ocupación media por temporada (%)

Temporada	Francia	Haute-Savoie	Diferencia
Entretiempo	52,3	52,9	+0,6
Invierno	46,0	61,4	+15,4
Verano	62,4	68,5	+6,1

Noches por origen del turista

	Turistas franceses	Turistas extranjeros	% extranjeros
Francia	920.985.420	480.729.320	34,3 %
Haute-Savoie	22.735.180	11.753.130	34,1 %

Correlación con la ocupación

Variable	Todo el año	Invierno	Verano
Temperatura media	0,56	0,42	0,08
Horas de sol	0,50	0,27	0,18
Nieve	-0,27	-0,22	-0,03
Viento máximo	-0,24	-0,21	0,07
Precipitación	-0,17	0,08	-0,23

Interpretación. 
Las correlaciones nacionales mezclan estación y geografía (los departamentos del sur son más cálidos y soleados), así que no demuestran que el buen tiempo llene los hoteles. La ventaja invernal de Haute-Savoie es coherente con su turismo de montaña, pero estos datos no permiten comprobarlo.

8. Dashboard
Dashboard en Google Sheets contiene:

Indicadores: ocupación media de Francia (52,8 %) y de Haute-Savoie (61,4 %) y noches totales.
Gráficos: ocupación por temporada, ocupación mensual, correlaciones, top de departamentos por ocupación y origen de los turistas (Francia frente a Haute-Savoie).
Pestaña "Conclusiones": hallazgos, interpretación y limitaciones.


9. Limitaciones
Los datos son solo de hoteles y alojamientos similares (código I551, según el metadata del Insee): no incluyen campings, residencias de turismo ni alquileres vacacionales.
La ocupación media es un promedio simple de departamentos y meses, sin ponderar por tamaño.
2020 y 2021 están afectados por la pandemia y algunos meses no tienen dato.
El clima de cada departamento se calcula en un punto (media de sus comunas), que no coincide con Chamonix.
La nieve procede de un modelo de reanálisis y puede estar infravalorada en zonas de montaña.
Los porcentajes de origen se calculan sobre las noches con desglose por origen disponible.
Los datos más recientes pueden ser provisionales (687 filas con estado P).
Correlación no implica causalidad.

10. Cómo reproducir el proyecto

Requisitos: Python 3, pandas y requests.

bash
pip install pandas requests

Ejecutar desde la raíz del repositorio, en este orden:

bash
python scripts/01_coordenadas.py
python scripts/01b_coordenadas_reintento.py    # solo si faltan departamentos
python scripts/02_descargar_clima.py           # puede requerir varios días
python scripts/03_limpiar_turismo.py
python scripts/04_unir_datasets.py
python scripts/05_analisis.py

El script 02 se detiene al alcanzar el límite diario de Open-Meteo: basta con volver a ejecutarlo al día siguiente. Los archivos en bruto ya están incluidos en data/raw/, por lo que se puede saltar directamente al paso 03.

11. Herramientas
Python y pandas para la obtención, limpieza, unión y análisis de los datos
Visual Studio Code como entorno de desarrollo
Google Sheets para el dashboard
GitHub para el repositorio
12. Autora

