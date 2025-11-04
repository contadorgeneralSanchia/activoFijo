import os, argparse, re, uuid
import pandas as pd
from dotenv import load_dotenv
from models import Activo, init_db, SessionLocal

def normalize_header(h: str) -> str:
    h = h.strip().lower()
    h = h.replace(" ", "_").replace("%", "pct").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")
    h = re.sub(r"[^a-z0-9_]", "", h)
    return h

def try_parse_date(x):
    if pd.isna(x):
        return None
    try:
        return pd.to_datetime(x).date().isoformat()
    except Exception:
        return str(x)

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Importa Excel de activos a SQLite")
    parser.add_argument("--excel", default=os.getenv("EXCEL_PATH", "data/activos.xlsx"))
    args = parser.parse_args()
    excel_path = args.excel

    if not os.path.exists(excel_path):
        raise SystemExit(f"No existe el archivo: {excel_path}")

    print(f"Leyendo archivo: {excel_path}")
    df = pd.read_excel(excel_path, engine="openpyxl")
    df.columns = [normalize_header(c) for c in df.columns]

    # Mostrar las columnas detectadas
    print("👉 Columnas detectadas:", df.columns.tolist())

    # Verificar las columnas clave
    if "codigo_activo_fijo" not in df.columns or "descripcion_activo_fijo" not in df.columns:
        raise SystemExit("❌ No se encontraron las columnas requeridas en el Excel.")

    # Crear columnas estándar
    df["codigo"] = df["codigo_activo_fijo"].astype(str).str.strip()
    df["nombre"] = df["descripcion_activo_fijo"].astype(str).str.strip()

    # Mostrar una muestra para confirmar
    print("\n👉 Primeras 5 filas después de asignar columnas 'codigo' y 'nombre':")
    print(df[["codigo", "nombre", "ubicacion", "departamento"]].head())

    # Normalizar fechas
    for dcol in ["fecha_adquisicion","fecha_inicio_uso"]:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(try_parse_date)

    for col in ["meses_a_depreciar","costo_adquisicion","valor_total_depreciar",
                "pct_depreciacion_anual","depreciacion_acumulada","saldo_por_depreciar"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Guardar en la base
    init_db()
    with SessionLocal() as db:
        count = 0
        for _, row in df.iterrows():
            codigo = row.get("codigo")
            if not codigo or codigo == "nan":
                continue
            activo = db.query(Activo).filter_by(codigo=codigo).first()
            if not activo:
                activo = Activo(codigo=codigo, qr_uid=str(uuid.uuid4()))
            activo.nombre = row.get("nombre")
            activo.fecha_adquisicion = row.get("fecha_adquisicion")
            activo.fecha_inicio_uso = row.get("fecha_inicio_uso")
            activo.meses_depreciacion = row.get("meses_a_depreciar")
            activo.ubicacion = row.get("ubicacion")
            activo.departamento = row.get("departamento")
            activo.serie = row.get("serie")
            activo.costo_adquisicion = row.get("costo_adquisicion")
            activo.total_depreciado = row.get("valor_total_depreciar")
            activo.pct_depreciacion_anual = row.get("pct_depreciacion_anual")
            activo.depreciacion_acumulada = row.get("depreciacion_acumulada")
            activo.saldo_por_depreciar = row.get("saldo_por_depreciar")
            db.add(activo)
            count += 1
        db.commit()

    print(f"\n✅ Importados o actualizados {count} registros correctamente.")

if __name__ == "__main__":
    main()
