from django.shortcuts import render
from django.http import HttpResponse

import PyPDF2
import nltk
import os
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from .models import Document
from .forms import DocumentForm


def clasificador(file):
    ##T ipos de hechos - firma del contrato :: Clasificacion -- Firma de contartos :: contrato
    tipo1=["firmar","susricribir","objeto","valor","obligacion","clausula"]
    distribucionTipo1=0
    #Modificaciones/ posibles :: actas y contarto
    tipo2=["otrosi","Adicion","agregar" ,"prórroga","ampliar","renovar","modificar","modificacion","renovar", "terminar", "finalizar", "concluir"]
    distribucionTipo2=0
    #ejecucion/pagos :: actas de pago, facturas, 
    tipo3=["orden de compra","actas","informes","pagos","facturas", "auditoria","interventor","supervisor","resolucion","suspencion"]
    distribucionTipo3=0
    #liquidacion/terminacion :: facturas, informes, pagos
    tipo4=["actas","informes","pagos","facturas", "auditorias","interventores","supervisores","suspencion"]
    distribucionTipo4=0

    #creamos un txt que almacene todo el contenido del pdf
    f= open("texto.txt","w+")

    #abriendo pdf in modo read binary(rb)
    #creo un objeto pdfReader (este permite es elque permite hacer las operaciones)
    pdfReader=PyPDF2.PdfFileReader(file)

    #numero de paginas del documento
    numeroDePaginasPdf=pdfReader.numPages

    #obteniendo pagina a pagina y añadiendo al arreglo de paginas
    #palabrasInutiles=stopwords.words("spanish")
    tokens=""
    for pagina in  range(numeroDePaginasPdf):
        paginaActual=pdfReader.getPage(pagina)
        #Extraigo todo el texto del pdf
        textoPagina=paginaActual.extractText()
        f.write(textoPagina)
    
    f.close()

    #abrimos el txt para tokenizar(dividir el texto en palabras)
    f = open("texto.txt","r")
    tokens=word_tokenize(f.read())

    #cerramos el txt
    f.close()

    ##Creamos un diccionario con la frecuencia distribuida(cuantas veces sale una palabra)
    frecuenciaDistribuida=FreqDist()
    for palabra in tokens:
        frecuenciaDistribuida[palabra.lower()]+=1

    ##aca va la parte de la clasificacion.
    for palabra in tipo1:
        if palabra in frecuenciaDistribuida:
            distribucionTipo1+=frecuenciaDistribuida.get(palabra)
    for palabra in tipo2:
        if palabra in frecuenciaDistribuida:
            distribucionTipo2+=frecuenciaDistribuida.get(palabra) 
    for palabra in tipo3:
        if palabra in frecuenciaDistribuida:
            distribucionTipo3+=frecuenciaDistribuida.get(palabra)  
    for palabra in tipo4:
        if palabra in frecuenciaDistribuida:
            distribucionTipo4+=frecuenciaDistribuida.get(palabra)                    

    resultado = []

    if distribucionTipo1>0:
        resultado.append({'t': 'Firma de contratos', 'info': 'Para la realización de una firma de contrato es necesario el respectivo contrato como evidencia de que de su elaboración.'})
    if distribucionTipo2>0:
        resultado.append({'t': 'Modificaciones', 'info': 'algo generico'})
    if distribucionTipo3>0:
        resultado.append({'t': 'Ejecución de Pagos', 'info': 'algo generico'})
    if distribucionTipo4>0:
        resultado.append({'t': 'Liquidación - Terminación', 'info': 'algo generico'})         
    if os.path.exists("texto.txt"):
        os.remove("texto.txt")  

    x = {'tipo1': distribucionTipo1, 'tipo2': distribucionTipo2, 'tipo3': distribucionTipo3, 'tipo4': distribucionTipo4, 'resultados': resultado}

    return  x





# Create your views here.
def index(request):
    dict = {}
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['docfile']
            print(f'--> * file :: %s' % docfile)
            dict = clasificador(docfile)
            print(dict)
            docfile.close()
    else:
        form = DocumentForm()

    # return HttpResponse('Hello from Python!')
    return render(request, "index.html", {'form': form, 'results': dict })



def info(request):
    return render(request, "info.html")


