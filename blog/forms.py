from django import forms

class ContactForm(forms.Form):
    annee_naissance_groupe = forms.CharField(help_text="Entrez une année de naissance",max_length=100,required=False)
    choix_liste_noms = forms.BooleanField(help_text="Cochez si vous souhaitez entrer une liste de nageurs à la place de l'année de naissance.", required=False)
    liste_nageurs = forms.CharField(help_text="Entrez une liste de nageurs sous la forme : 'NOM1 Prénom1/NOM2 Prénom2/NOM3 Prénom3/../' sans espaces entre les //, le NOM en majuscule et le Prénom avec seulement la première lettre en majuscule et en conservant les accents si il y en a.",widget=forms.Textarea,required=False)
    nom_du_groupe =  forms.CharField(max_length=100,required=True)