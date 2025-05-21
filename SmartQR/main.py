from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class QRData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    qr_base64 = None

    if request.method == "POST":
        data = request.form["data"]
        if data:
    
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        
            new_entry = QRData(user_input=data)
            db.session.add(new_entry)
            db.session.commit()

    return render_template("index.html", qr_image=qr_base64)

@app.route("/history")
def history():
    all_qrs = QRData.query.order_by(QRData.created_at.desc()).all()
    return render_template("history.html", qrs=all_qrs)

if __name__ == "__main__":
    app.run(debug=True)
