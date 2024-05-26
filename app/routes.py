from app import app
from flask import render_template, request, flash, redirect
import os
from werkzeug.utils import secure_filename
from mapa import mapa
from classificador import prediction_func
from database import db
from models import Solicitacao


#from models import Usuario

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/envio_de_foto')
def envio_de_foto():
    return render_template('envio_de_foto.html')

@app.route('/resultado_da_consulta', methods=['POST'])
def resultado_da_consulta():
    nome = request.form.get('nome')
    email = request.form.get('email')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    img = request.files['file']

    # Save the image to ./uploads
    basepath = os.path.dirname(__file__)
    img_dir = os.path.join(
        basepath, 'uploads', secure_filename(img.filename))
    img.save(img_dir)

    # Make prediction
    preds = prediction_func(img_dir)
    dl_classification = preds.split('\n')[0]

    solicitacao = Solicitacao(nome, email, telefone, endereco, dl_classification, img_dir)
    db.session.add(solicitacao)
    db.session.commit()

    return None

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario == 'admin' and senha == 'senha123':
        # Mostrar o formulario onde o especialista poderá preencher sua classificação 
        # e ver o mapa com os marcadores de envios de fotos indicando se já foram 
        # classificadas por um especialista
        nome = list(('joao', 'ana'))
        email = list(('asdsad@fasd.com', 'asdasf@grsf.com'))
        telefone = list(('2132312321', '4123231123'))
        endereco = list(('rua lauro muller, 36', 'rua dias cabral, 82'))
        nivel_certeza = list(('ALTA', 'BAIXA'))
        real_classification = list((True, ''))
        nome_especialista = list(('pedro', ''))
        img_dir = list(('D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta.jpg', 
                        'D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta2.jpg'))
        
        mapa(nome,email,telefone,endereco,nivel_certeza,real_classification,nome_especialista,img_dir)
        
        return render_template('especialista.html')
    else:
        flash("Dados inválidos")
        flash("Login ou senha inválidos")
        return redirect('/login')
    
    # u = Usuario(nome, email, senha)
    # db.session.add(u)
    # db.session.commit()
    # return 'Dados cadastrados com sucesso'
