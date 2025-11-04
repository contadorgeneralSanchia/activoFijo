import os, argparse, qrcode
from dotenv import load_dotenv
from models import SessionLocal, Activo
load_dotenv()
def main():
    parser = argparse.ArgumentParser(description="Genera PNGs QR únicos para cada activo")
    parser.add_argument("--host", required=True, help="URL base (ej: http://127.0.0.1:5000)")
    parser.add_argument("--out", default="static/qr", help="Carpeta de salida para PNGs")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    with SessionLocal() as db:
        activos = db.query(Activo).all()
        for a in activos:
            url = f"{args.host}/asset/qr/{a.qr_uid}"
            safe_code = (a.codigo or f"id{a.id}").replace("/", "_").replace("\\", "_").replace(" ", "_")
            fname = os.path.join(args.out, f"{safe_code}_{a.qr_uid}.png")
            if not os.path.exists(fname):
                img = qrcode.make(url)
                img.save(fname)
                print(f"[QR creado] {fname}  ({url})")
            else:
                print(f"[Existe] {fname}")
if __name__ == "__main__":
    main()
