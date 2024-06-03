import folium
from geopy.geocoders import Nominatim
import base64
import os
from werkzeug.utils import secure_filename

def mapa(nome,email,telefone,logradouro,numero,municipio,estado,
         latitude,longitude,nivel_certeza,real_classification,nome_especialista,img_dir):
    
    map = folium.Map(location=[-23.0, -43.0], zoom_start=8)
    fg = folium.FeatureGroup(name="Mapa de fotos enviadas no portal").add_to(map)

    for nome,email,telefone,logradouro,numero,municipio,estado,latitude,longitude,nivel_certeza,real_classification,nome_especialista,img_dir in zip(nome,email,telefone,logradouro,numero,municipio,estado,latitude,longitude,nivel_certeza,real_classification,nome_especialista,img_dir):
        # loc = Nominatim(user_agent="GetLoc")
        # getLoc = loc.geocode(endereco)
        # lat = getLoc.latitude
        # long = getLoc.longitude

        encoded = base64.b64encode(open(img_dir, 'rb').read()).decode()
        html = f'''<b>Nome:</b><br>
                {nome}<br>
                <b>Email:</b><br>
                {email}<br>
                <b>Telefone:</b><br>
                {telefone}<br>
                <b>Endereço:</b><br>
                {logradouro+', '+numero+', '+municipio+', '+estado}<br>
                <b>Chance de ser barbeiro:</b><br>
                {nivel_certeza}<br>
                <br>
                <img src="data:image/jpeg;base64,{encoded}" width=200px>'''

        iframe = folium.IFrame(html,width=350,height=450)
        popup = folium.Popup(iframe,max_width=450)
        if latitude != None and longitude != None:
            if real_classification == None:
                marker = folium.Marker([latitude,longitude], popup=(popup),
                                    icon=folium.Icon(icon='exclamation-sign',icon_color='red',color='black')).add_to(map)
            else:
                marker = folium.Marker([latitude,longitude], popup=(popup), 
                                    icon=folium.Icon(icon='ok',icon_color='green',color='black')).add_to(map)

            map.add_child(marker)

    basepath = os.path.dirname(__file__)
    html_dir = os.path.join(
        basepath, 'app\\templates', secure_filename('especialista.html'))
    map.save(html_dir)
    #map.save('D:/fiocruz/aplicacao_web/app/templates/especialista.html')