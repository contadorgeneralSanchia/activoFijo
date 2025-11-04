import os
from flask import Flask, render_template, abort
from dotenv import load_dotenv
from models import SessionLocal, Activo, init_db
load_dotenv()
TITLE = os.getenv("APP_TITLE", "Registro de Activo Fijo")
app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
init_db()
@app.context_processor
def inject_globals():
    return {"APP_TITLE": TITLE}
@app.get("/")
def index():
    with SessionLocal() as db:
        activos = db.query(Activo).order_by(Activo.id.asc()).all()
        count = len(activos)
    return render_template("index.html", all=activos, count=count)

@app.get("/asset/<int:asset_id>")
def asset_detail(asset_id: int):
    with SessionLocal() as db:
        activo = db.query(Activo).filter(Activo.id == asset_id).first()
        if not activo:
            return "Activo no encontrado", 404
    return render_template("asset_detail.html", activo=activo)


@app.get("/asset/qr/<string:qr_uid>")
def asset_by_qr(qr_uid):
    """Permite abrir la ficha del activo al escanear su QR"""
    with SessionLocal() as db:
        activo = db.query(Activo).filter_by(qr_uid=qr_uid).first()
        if not activo:
            return "QR no válido o activo no encontrado", 404
    return render_template("asset_detail.html", activo=activo)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
