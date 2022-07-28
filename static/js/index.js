
var imagen_random = new Array();
imagen_random[0] = "images/1.jpg";
imagen_random[1] = "images/2.jpg";
imagen_random[2] = "images/3.jpg";
imagen_random[3] = "images/4.jpg";
imagen_random[4] = "images/5.jpg";


function cargar_imagen_random() {
    //document.images["random"].src = imagen_random[azar];
    document.querySelectorAll('div > img').forEach(function (imagen) {
        var azar = Math.floor(Math.random() * imagen_random.length);
        imagen.src = imagen_random[azar];
    });
}