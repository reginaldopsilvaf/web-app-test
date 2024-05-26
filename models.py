from database import db

class Solicitacao(db.Model):
    __tablename__='solicitacao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(100))
    dl_classification = db.Column(db.String(10))
    especialista_classification = db.Column(db.String(8))
    nome_especialista = db.Column(db.String(50))
    img_dir = db.Column(db.String(50))

    def __init__(self, nome, email, telefone, endereco, 
                 dl_classification, especialista_classification=None, nome_especialista=None, img_dir):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.endereco = endereco
        self.dl_classification = dl_classification
        self.especialista_classification = especialista_classification
        self.nome_especialista = nome_especialista
        self.img_dir = img_dir

    def __repr__(self):
        return "Solicitação: {}".format(self.id)