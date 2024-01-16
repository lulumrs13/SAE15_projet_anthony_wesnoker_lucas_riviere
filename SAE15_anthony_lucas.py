import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
from icalendar import Calendar

def convertir_ics_vers_csv(chemin_fichier_ics, chemin_fichier_csv):
    # Lire le fichier .ics
    with open(chemin_fichier_ics, 'rb') as fichier_ics:
        cal = Calendar.from_ical(fichier_ics.read())

    # Créer et écrire dans le fichier .csv
    with open(chemin_fichier_csv, 'w', encoding='utf-8') as fichier_csv:
        wr = csv.writer(fichier_csv)
        wr.writerow(['RESUME', 'DEBUT', 'FIN', 'DESCRIPTION'])

        for composant in cal.walk():
            if composant.name == "VEVENT":
                resume = str(composant.get('summary'))
                debut = composant.get('dtstart').dt.strftime('%Y-%m-%d %H:%M:%S') if composant.get('dtstart') else ''
                fin = composant.get('dtend').dt.strftime('%Y-%m-%d %H:%M:%S') if composant.get('dtend') else ''
                description = str(composant.get('description'))
                wr.writerow([resume, debut, fin, description])

chemin_fichier_ics = '/home/etudiant/Bureau/ADECal.ics'
chemin_fichier_csv = '/home/etudiant/Bureau/ADEconv.csv'

# Vérifier que le fichier existe
if not os.path.exists(chemin_fichier_ics):
    print("Le fichier .ics spécifié n'existe pas.")
else:
    convertir_ics_vers_csv(chemin_fichier_ics, chemin_fichier_csv)
    print("La conversion est terminée. Le fichier CSV est sauvegardé à :", chemin_fichier_csv)

# Tableau avec le nom des professeurs
noms_professeurs = [
    "ZIMMER CHRISTINE", "AZZOUNI SOUMAYA", "CHABOT ROBERT",
    "DEPREZ JEAN-LUC", "VIOIX JEAN-BAPTISTE", "PRESLES BENOÎT",
    "NECTOUX ANTOINE", "MARCEL SEVERINE", "CHANAMBEAU CHRISTINE",
    "PERNOT ANTOINE", "ROY MICHAEL", "ANSEL DAVID",
    "PETITPRE KAREEN", "CARTIER ANNA", "TROUTTET SYLVAIN"
]

# Lire le fichier CSV
chemin_fichier_csv = '/home/etudiant/Bureau/ADEconv.csv'
with open(chemin_fichier_csv, mode='r', encoding='utf-8') as fichier:
    lecteur = csv.reader(fichier)
    donnees_csv = list(lecteur)

# Analyser les horaires des cours à partir des données CSV
def analyser_horaires_cours(donnees_csv, noms_professeurs):
    horaires_cours = {nom: [] for nom in noms_professeurs}
    for ligne in donnees_csv[1:]:  # Ignorer l'en-tête
        debut = datetime.strptime(ligne[1], '%Y-%m-%d %H:%M:%S')
        fin = datetime.strptime(ligne[2], '%Y-%m-%d %H:%M:%S')
        for nom in noms_professeurs:
            if nom in ligne[3]:
                horaires_cours[nom].append((ligne[0], debut, fin))
    return horaires_cours

# Fonction pour vérifier s'il y a des vacances ou non (condition de 6 jours consécutifs)
def calculer_details_vacances(cours):
    cours.sort(key=lambda x: x[1])  # Trier par heure de début
    details_vacances = []
    for i in range(1, len(cours)):
        ecart = cours[i][1] - cours[i-1][2]
        if ecart >= timedelta(days=6):
            details_vacances.append({
                'titre_dernier_cours': cours[i-1][0],
                'fin_dernier_cours': cours[i-1][2],
                'titre_premier_cours_apres_vacances': cours[i][0],
                'debut_premier_cours': cours[i][1],
                'longueur_vacances': ecart.days
            })
    return details_vacances

# Fonction pour créer l'histogramme des vacances
def creer_histogramme_vacances(details_vacances, nom_professeur):
    longueurs_vacances = [detail['longueur_vacances'] for detail in details_vacances]
    plt.bar(range(len(longueurs_vacances)), longueurs_vacances)
    plt.xlabel('Période de Vacances')
    plt.ylabel('Jours')
    plt.title(f'Longueur des Vacances de {nom_professeur}')
    plt.savefig(f'/home/etudiant/Bureau/{nom_professeur}_histogramme_vacances.png')

# Créer un fichier CSV pour le détail des vacances
def ecrire_details_vacances_csv(details_vacances, nom_professeur, chemin_fichier_csv):
    with open(chemin_fichier_csv, mode='w', newline='', encoding='utf-8') as fichier:
        wr = csv.writer(fichier)
        wr.writerow(['Titre du Dernier Cours', 'Fin du Dernier Cours', 'Titre du Premier Cours Après les Vacances', 'Début du Premier Cours', 'Longueur des Vacances'])
        for detail in details_vacances:
            wr.writerow([
                detail['titre_dernier_cours'],
                detail['fin_dernier_cours'].strftime('%Y-%m-%d %H:%M:%S'),
                detail['titre_premier_cours_apres_vacances'],
                detail['debut_premier_cours'].strftime('%Y-%m-%d %H:%M:%S'),
                detail['longueur_vacances']
            ])

# Demander à l'utilisateur quel professeur il souhaite voir les détails des vacances
print("Choisissez un professeur pour voir les détails de ses vacances :")
for i, nom in enumerate(noms_professeurs, 1):
    print(f"{i}. {nom}")
indice_selectionne = int(input("Entrez le numéro correspondant au professeur : ")) - 1
nom_professeur_selectionne = noms_professeurs[indice_selectionne]

# Donner les détails pour le professeur choisi
horaires_cours = analyser_horaires_cours(donnees_csv, [nom_professeur_selectionne])[nom_professeur_selectionne]
details_vacances = calculer_details_vacances(horaires_cours)

# Générer un histogramme et un fichier CSV pour le professeur sélectionné
creer_histogramme_vacances(details_vacances, nom_professeur_selectionne)
chemin_csv_sortie = f'/home/etudiant/Bureau/{nom_professeur_selectionne}_details_vacances.csv'
ecrire_details_vacances_csv(details_vacances, nom_professeur_selectionne, chemin_csv_sortie)
