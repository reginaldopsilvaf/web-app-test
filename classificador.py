import tensorflow as tf
import numpy as np
from keras.applications.imagenet_utils import preprocess_input

def prediction_func(img_path):

    # Model saved with Keras model.save()
    MODEL_PATH = 'D:/fiocruz/aplicacao_web/app/modelo_classificador/model_resnet18.keras'
    # Load your trained model
    model = tf.keras.models.load_model(MODEL_PATH)

    img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
    #img_4d=img.reshape(-1,224,224,3)
    x = tf.keras.utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x, mode='caffe')
    output = np.array(tf.nn.softmax(model.predict(x)))[0] * 100

    nivel_certeza = ''

    if output[1] < 55.0:
        nivel_certeza = 'BAIXA'
    elif (output[1] >= 55.0 and output[1] < 70.0):
        nivel_certeza = 'MEDIA'
    elif (output[1] >= 70.0 and output[1] < 85.0):
        nivel_certeza = 'MODERADA'
    elif (output[1] >= 85.0 and output[1] < 95.0):
        nivel_certeza = 'ALTA'
    elif output[1] >= 95.0:
        nivel_certeza = 'ALTISSIMA'

    nivel_certeza += f'\nSua foto demonstra uma {nivel_certeza} chance de ser um barbeiro.\n'
    nivel_certeza += 'A identificação será confirmada por um especialista e em breve voce receberá uma mensagem de confirmação.\n\n'
    nivel_certeza +=  'Siga as recomendações abaixo:\n\n'
    nivel_certeza +=  '1 - Proteja suas mãos usando um saco ou sacola plástica, assim você irá evitar o contato direto com o inseto;\n'
    nivel_certeza +=  '2 - Nunca tente matar ou esmagar o inseto, essa ação pode levar ao aumento do risco.\n'
    nivel_certeza +=  '3 - Recolha cuidadosamente o isento e coloque em um recipiente seco e tampado. Caso o inseto esteja vivo, realizar pequenos furos na tampa para possibilitar a ventilação.\n'
    nivel_certeza +=  'Caso o inseto ainda esteja no local deve ser levado, preferencialmente vivo, dentro de um frasco plástico lacrado para o PIT (Posto de identificação de Triatomíneos) mais próximo de sua residência\n'
    nivel_certeza +=  '(veja a localização dos PITs em:  https://chagas.fiocruz.br/entregue-pessoalmente).\n\n'
    nivel_certeza +=  'Caso não encontre um PIT próximo, oriento a entrar em contato com o órgão de saúde do seu município informando sobre o encontro do inseto, para que sejam tomadas as providências cabíveis.\n'
    nivel_certeza +=  'O inseto não deve ser manuseado com as mãos desprotegidas.'

    return nivel_certeza