from django.shortcuts import render

from django.http import HttpResponse

def home(request):
    device = request.META
    """ Exemple de page HTML, non valide pour que l'exemple soit concis """
    text = """<h1>Bienvenue sur mon blog !</h1>
              <p>Les crêpes bretonnes ça tue des mouettes en plein vol !</p>"""
    return HttpResponse("Wesh Flo, voici les infos sur ta connexion que j'ai réussi à"
                        " récupérer : ///////  TON IP :  \n"+device['REMOTE_ADDR']+"///////  TES DEVICE INFOS :"+request.META['HTTP_USER_AGENT'])