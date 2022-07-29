from flask import Flask, render_template,request, url_for, redirect, make_response, jsonify
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from random import randint
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from svg_turtle import SvgTurtle



# Configuración de formatos de archivo permitidos
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp', 'jpeg', 'JPEG'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#-----------------------Funciones para el analisis de la imagen ----------------------------

#-----rangos de color HSV -----

#Color Azul_1
lower_Azul_1= np.array([85, 100, 100])
upper_Azul_1 = np.array([98, 255, 255])
#Color Azul_2
lower_Azul_2= np.array([98, 100, 70])
upper_Azul_2 = np.array([140, 255, 255])

#Color Amarillo
lower_Amarillo = np.array([19, 100, 100])#valor anterios 20,100,100
upper_Amarillo = np.array([45, 255, 255])

#Color Rosa
lower_Rosa = np.array([145, 0, 30])
upper_Rosa = np.array([170, 255, 255])

#Color Verde
lower_Verde = np.array([50, 85, 50])#Valor anterior 45,100,50
upper_Verde = np.array([85, 255, 255])

#Color Rojo
lower_Rojo_1 = np.array([170, 50, 60])
upper_Rojo_1 = np.array([179, 255, 255])
lower_Rojo_2 = np.array([0, 100, 20])
upper_Rojo_2 = np.array([5, 255, 255])

#Color Naranja
lower_Naranja = np.array([6, 100, 200])# valor anterior 6,100,210
upper_Naranja = np.array([20, 255, 255])

#ColorMorado
lower_Morado = np.array([120, 30, 20])
upper_Morado = np.array([154, 255, 255])


#Figura Seleccionada
figura = 0

#Funcion para la extraccion de color
def extractColorImageHSV(image, lower_color, upper_color):
    (img_rows, img_cols, img_capas) = image.shape
    imagenVacia = np.zeros((img_rows, img_cols, img_capas), np.uint8)
    # se convierte la imagen a hsv
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # se crea la máscara
    mask = cv2.inRange(image_hsv, lower_color, upper_color)

    # Se realiza la operación AND
    res = cv2.bitwise_and(image, image, mask=mask)
    return (mask, res)

def dibujarContorno(img,contornos, color):
    bloques = {}
    i = 0
    for c in contornos:
        area = cv2.contourArea(c)#determinar el área en pixeles del contorno.
        if area > 20000:#solo tomamos areas mayores a 3000 pixeles
            M = cv2.moments(c) #con este vamos a encontrar los puntos centrales x e y del contorno.
            if (M["m00"]==0): M["m00"]==1
            x = int(M["m10"]/M["m00"])
            y = int(M["m01"]/M["m00"])
            cv2.drawContours(img, [c], 0, color, 2)
            cv2.putText(img, str((y,x)), (x-10,y+10), 1, 2,(0,0,0),2)
            bloques[i+1] = y
            i +=1
    return (bloques, img)


def ordenarBloques(bloques, color, dictBloques):
    if bloques != {}:
        sortedBloques = sorted(bloques.values())
        for pos_y in sortedBloques:
            dictBloques[pos_y] = color

        return dictBloques
    else:
        #print('no hay, no exixte')
        return dictBloques

blanco=(255,255,255)

app = Flask(__name__)
# Establecer el tiempo de caducidad de la caché de archivos estáticos
app.send_file_max_age_default = timedelta(seconds=1)

@app.route('/subir', methods = ['POST','GET'])
def subir():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "Verifique el tipo de imagen cargada, solo png, PNG, jpg, JPG, bmp"})

        basepath = os.path.dirname(__file__)  # ruta del archivo actual

        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))
        f.save(upload_path)

        # Use Opencv para convertir el formato y el nombre de la imagen
        img = cv2.imread(upload_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #img = cv2.medianBlur(img, 3)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'imgSubida.png'),
                    cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return render_template('img_subida.html')
    return render_template('index.html')


@app.route('/compilar')
def compilar():
    bloques={}
    basepath = os.path.dirname(__file__)  # ruta del archivo actual

    img_path = os.path.join(basepath, 'static/images', 'imgSubida.png')
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    (mascaraAzul_1, resultadoAzul_1) = extractColorImageHSV(img, lower_Azul_1, upper_Azul_1)
    #(mascaraAzul_2, resultadoAzul_2) = extractColorImageHSV(img, lower_Azul_2, upper_Azul_2)
    (mascaraAmarillo, resultadoAmarillo) = extractColorImageHSV(img, lower_Amarillo, upper_Amarillo)
    (mascaraRosa, resultadoRosa) = extractColorImageHSV(img, lower_Rosa, upper_Rosa)
    (mascaraRojo1, resultado1) = extractColorImageHSV(img, lower_Rojo_1, upper_Rojo_1)
    (mascaraRojo2, resultado2) = extractColorImageHSV(img, lower_Rojo_2, upper_Rojo_2)
    mascaraRojo = cv2.add(mascaraRojo1, mascaraRojo2)
    resultadoRojo =cv2.add(resultado1, resultado2)
    (mascaraVerde, resultadoVerde) = extractColorImageHSV(img, lower_Verde, upper_Verde)
    (mascaraNaranja, resultadoNaranja) = extractColorImageHSV(img, lower_Naranja, upper_Naranja)
    #(mascaraMorado, resultado) = extractColorImageHSV(img, lower_Morado, upper_Morado)
    
    contornosAzul_1 = cv2.findContours(mascaraAzul_1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesAzules_1, img) = dibujarContorno(img, contornosAzul_1, blanco)
    bloques = ordenarBloques(bloquesAzules_1, 'azul_1', bloques)
    #contornosAzul_2 = cv2.findContours(mascaraAzul_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    #(bloquesAzules_2, img) = dibujarContorno(img, contornosAzul_2, blanco)
    #bloques = ordenarBloques(bloquesAzules_2, 'azul_2', bloques)
    contornosAmarillo = cv2.findContours(mascaraAmarillo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesAmarillos, img)= dibujarContorno(img, contornosAmarillo, blanco)
    bloques = ordenarBloques(bloquesAmarillos, 'amarillo', bloques)
    contornosRosa = cv2.findContours(mascaraRosa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesRosas, img) = dibujarContorno(img, contornosRosa, blanco)
    bloques = ordenarBloques(bloquesRosas, 'rosa', bloques)
    contornosVerde = cv2.findContours(mascaraVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesVerdes, img) = dibujarContorno(img, contornosVerde, blanco)
    bloques = ordenarBloques(bloquesVerdes, 'verde', bloques)
    contornosRojo = cv2.findContours(mascaraRojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesRojos, img) = dibujarContorno(img, contornosRojo, blanco)
    bloques = ordenarBloques(bloquesRojos, 'rojo', bloques)
    contornosNaranja = cv2.findContours(mascaraNaranja, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    (bloquesNaranjas, img) = dibujarContorno(img, contornosNaranja, blanco)
    bloques = ordenarBloques(bloquesNaranjas, 'naranja', bloques)
    #contornosMorado = cv2.findContours(mascaraMorado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    #(bloquesMorado, img) = dibujarContorno(img, contornosMorado, blanco)
    #bloques = ordenarBloques(bloquesMorado, 'morado', bloques)

    bloques_sort = sorted(bloques.items())
    #print(bloques_sort)
    global figura
    print(figura)
    if bloques_sort[0][1] == 'rosa':  # Si el bloque ejecutar es el primero
        for i in bloques_sort:
            color = i[1]
            if color == 'rosa':
                t = SvgTurtle(500, 500)
                t.penup()
                if figura == 1:
                    t.sety(-100)
                    t.setx(-50)
                elif figura == 2:
                    t.sety(50)
                    t.setx(-50)
                elif figura == 3:
                    t.sety(50)
                    t.setx(-50)
                elif figura == 4:
                    t.sety(80)
                    t.setx(-50)
                elif figura == 5:#Se cambiaron los valores de inicio por los del rombo
                    t.sety(50)
                    t.setx(0)
                else:
                    t.sety(50)
                    t.setx(-50)
                t.pendown()
                t.pensize(10)
                t.color('blue')
            if color == 'amarillo':
                t.forward(100)  # Avanza 200px
            if color == 'azul_1':
                t.left(120)  # Gira a la derecha 120°
            #if color == 'azul_2':
                #t.left(110)  # Gira a la izquierda 110°
            if color == 'rojo':
                t.right(60)  # Gira a la derecha 60°
            if color == 'verde':
                t.right(90)  # Gira a la derecha 90°
            if color == 'naranja':
                t.right(120)  # Gira a la derecha 60°
            #if color == 'morado':
                #t.left(70)  # Gira a la izquierda 70°
    else:
        print('Bloque ejecutar no esta en la posción inicial.')
    
    svg_path = os.path.join(basepath, 'static/images', 'resultado.svg')
    t.save_as(svg_path)
    resultado_path = os.path.join(basepath, 'static/images', 'resultado.png')
    drawing = svg2rlg(svg_path)
    renderPM.drawToFile(drawing, resultado_path, fmt='PNG')

    cv2.imwrite(os.path.join(basepath, 'static/images', 'Contornos.png'), cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    return render_template('resultados.html')

@app.route('/imgAleatoria')
def imgAleatoria():
    num = randint(1,4)# genera un numero random del 1 al 4
    #print(num)

    basepath = os.path.dirname(__file__)  # ruta del archivo actual
    random_path = os.path.join(basepath, 'static/images', str(num) + '.png')
    ram =  cv2.imread(random_path)
    ram = cv2.cvtColor(ram, cv2.COLOR_BGR2RGB)
    cv2.imwrite(os.path.join(basepath, 'static/images', 'figuraSeleccionada.png'), cv2.cvtColor(ram, cv2.COLOR_BGR2RGB))
    global figura
    figura = num
    data = 'figuraSeleccionada.png'
    return render_template('index.html', data = data)


@app.route("/")
def Index():
    data = 'inicio.png'
    return render_template('index.html', data = data)


if __name__ == '__main__':
    app.run(port=3000, debug=True)