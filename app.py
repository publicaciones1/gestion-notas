from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

# Configuración DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo
class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linea = db.Column(db.String(100), nullable=False)
    redes = db.Column(db.String(100), nullable=False)
    periodista = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    medio = db.Column(db.String(255), nullable=False)
    enlace = db.Column(db.String(500))
    fecha = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

# Página principal
@app.route('/')
def index():
    notas = Nota.query.all()
    return render_template('index.html', notas=notas)

# Agregar nota
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        try:
            linea = request.form.get('linea')
            redes = request.form.get('redes')
            periodista = request.form.get('periodista')
            titulo = request.form.get('titulo')
            medio = ", ".join(request.form.getlist('medio'))
            enlace = request.form.get('enlace')

            if not (linea and redes and periodista and titulo and medio):
                flash("⚠ Todos los campos son obligatorios.")
                return redirect(url_for('add_note'))

            nueva_nota = Nota(
                linea=linea,
                redes=redes,
                periodista=periodista,
                titulo=titulo,
                medio=medio,
                enlace=enlace
            )
            db.session.add(nueva_nota)
            db.session.commit()
            flash("✅ Nota guardada con éxito.")
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"❌ Error al guardar: {str(e)}")
            return redirect(url_for('add_note'))

    return render_template('add_note.html')

# Editar nota
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    nota = Nota.query.get_or_404(id)
    if request.method == 'POST':
        try:
            nota.linea = request.form.get('linea')
            nota.redes = request.form.get('redes')
            nota.periodista = request.form.get('periodista')
            nota.titulo = request.form.get('titulo')
            nota.medio = ", ".join(request.form.getlist('medio'))
            nota.enlace = request.form.get('enlace')

            db.session.commit()
            flash("✅ Nota actualizada con éxito.")
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"❌ Error al actualizar: {str(e)}")
            return redirect(url_for('edit_note', id=id))

    return render_template('edit_note.html', nota=nota)

# Eliminar nota
@app.route('/delete/<int:id>', methods=['POST'])
def delete_note(id):
    try:
        nota = Nota.query.get_or_404(id)
        db.session.delete(nota)
        db.session.commit()
        flash("🗑 Nota eliminada con éxito.")
    except Exception as e:
        flash(f"❌ Error al eliminar: {str(e)}")
    return redirect(url_for('index'))

# Exportar a Excel
@app.route('/export')
def export_excel():
    notas = Nota.query.all()
    if not notas:
        return "No hay datos para exportar."

    data = [{
        'Línea': n.linea,
        'Redes': n.redes,
        'Periodista': n.periodista,
        'Título': n.titulo,
        'Medio': n.medio,
        'Enlace': n.enlace,
        'Fecha': n.fecha.strftime('%d/%m/%Y')
    } for n in notas]

    df = pd.DataFrame(data)
    file_path = "notas_exportadas.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

