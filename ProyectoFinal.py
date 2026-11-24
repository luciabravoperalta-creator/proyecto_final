import pandas as pd

df = pd.read_csv("data/processed/dataset_final_francia.csv", dtype={"GEO": str})

# ---------- 1. Validación ----------
print("Forma:", df.shape)
clave = ["GEO", "TOUR_RESID", "TOUR_MEASURE", "TIME_PERIOD"]
print("Duplicados:", df.duplicated(subset=clave).sum())
print("Nulos totales:", df.isna().sum().sum())
print("Años:", df["anio"].min(), "-", df["anio"].max(),
      "| Departamentos:", df["GEO"].nunique())

total = df[df["TOUR_RESID"] == "_T"]
ocup = total[total["TOUR_MEASURE"] == "PLACE_OCCUPANCY_RATE"].copy()
noches = total[total["TOUR_MEASURE"] == "NIGHT_SPENT"].copy()
print("Filas de ocupación:", len(ocup), "| filas de noches:", len(noches))
print("Ocupación entre", ocup["valor_real"].min(), "y", ocup["valor_real"].max())

control = ocup[(ocup["GEO"] == "74") & (ocup["TIME_PERIOD"] == "2022-01")]
print("Control Haute-Savoie 2022-01 (esperado 50.0):",
      control["valor_real"].tolist())

hs = ocup[ocup["GEO"] == "74"]

# ---------- 2. Tablas resumen ----------
# a) Por temporada
t = ocup.groupby("temporada")["valor_real"].mean().rename("Francia").to_frame()
t["Haute-Savoie"] = hs.groupby("temporada")["valor_real"].mean()
t = t.round(1).reset_index()
t.to_csv("data/processed/resumen_temporada.csv", index=False)
print("\nOcupación media por temporada (%):\n", t)

# b) Por mes
m = ocup.groupby("TIME_PERIOD").agg(
    ocupacion_francia=("valor_real", "mean"),
    temp_media_francia=("temp_media", "mean")).round(1)
m["ocupacion_haute_savoie"] = hs.set_index("TIME_PERIOD")["valor_real"]
m.reset_index().to_csv("data/processed/resumen_mensual.csv", index=False)

# c) Por departamento
dep = ocup.groupby(["GEO", "departamento"]).agg(
    ocupacion_media=("valor_real", "mean"),
    temp_media=("temp_media", "mean"),
    precip_media=("precip_total", "mean"),
    nieve_media=("nieve_total", "mean")).round(1).reset_index()
nt = noches.groupby("GEO")["valor_real"].sum().rename("noches_totales")
dep = dep.merge(nt, on="GEO", how="left")
dep = dep.sort_values("ocupacion_media", ascending=False)
dep.to_csv("data/processed/resumen_departamentos.csv", index=False)
print("\nTop 10 departamentos por ocupación:\n", dep.head(10)[["departamento", "ocupacion_media"]])

# d) Origen: Francia vs Extranjero (categorías que no se solapan)
o = df[(df["TOUR_MEASURE"] == "NIGHT_SPENT")
       & (df["TOUR_RESID"].isin(["250", "1_X_250"]))].copy()
o["origen"] = o["TOUR_RESID"].map({"250": "Francia", "1_X_250": "Extranjero"})
tabla_o = o.groupby("origen")["valor_real"].sum().rename("Francia (todos)").to_frame()
tabla_o["Haute-Savoie"] = o[o["GEO"] == "74"].groupby("origen")["valor_real"].sum()
tabla_o.reset_index().to_csv("data/processed/resumen_origen.csv", index=False)
print("\nNoches por origen:\n", tabla_o)

# ---------- 3. Correlaciones con la ocupación ----------
vars_clima = ["temp_media", "precip_total", "nieve_total", "horas_sol", "viento_max"]
corr = ocup[vars_clima + ["valor_real"]].corr()["valor_real"].drop("valor_real")
corr = corr.rename("Todo el año").to_frame()
for temp in ["Invierno", "Verano"]:
    s = ocup[ocup["temporada"] == temp]
    corr[temp] = s[vars_clima + ["valor_real"]].corr()["valor_real"].drop("valor_real")
corr = corr.round(2).reset_index().rename(columns={"index": "variable"})
corr.to_csv("data/processed/resumen_correlaciones.csv", index=False)
print("\nCorrelación con la ocupación:\n", corr)