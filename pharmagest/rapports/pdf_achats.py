import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime

def generer_bon_commande_pdf(commande):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(15*mm, height - 20*mm, "PHARMAGEST")
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 26*mm, "Antananarivo, Madagascar")
    p.drawString(15*mm, height - 31*mm, "Tél: +261 34 00 000 00")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(15*mm, height - 45*mm, f"BON DE COMMANDE N° {commande.reference}")
    
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 52*mm, f"Date : {commande.date_commande.strftime('%d/%m/%Y')}")
    p.drawString(15*mm, height - 57*mm, f"Fournisseur : {commande.fournisseur.nom}")
    p.drawString(15*mm, height - 62*mm, f"Adresse : {commande.fournisseur.adresse or '-'}")
    p.drawString(15*mm, height - 67*mm, f"Téléphone : {commande.fournisseur.telephone or '-'}")

    y = height - 80*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Médicament")
    p.drawString(85*mm, y, "Qté")
    p.drawString(110*mm, y, "Prix U. (Ar)")
    p.drawString(145*mm, y, "Sous-total (Ar)")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    for ligne in commande.lignes.all():
        y -= 7*mm
        if y < 20*mm:
            p.showPage()
            y = height - 20*mm
        p.drawString(15*mm, y, ligne.medicament.nom_commercial[:40])
        p.drawString(85*mm, y, str(ligne.quantite_commandee))
        p.drawString(110*mm, y, f"{ligne.prix_achat_unitaire}")
        p.drawString(145*mm, y, f"{ligne.sous_total}")

    y -= 10*mm
    p.line(15*mm, y, width - 15*mm, y)
    y -= 8*mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(110*mm, y, "TOTAL :")
    p.drawString(145*mm, y, f"{commande.total_commande} Ar")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generer_bon_reception_pdf(commande):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(15*mm, height - 20*mm, "PHARMAGEST")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(15*mm, height - 35*mm, f"BON DE RÉCEPTION - Commande {commande.reference}")
    
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 42*mm, f"Date d'impression : {datetime.now().strftime('%d/%m/%Y')}")
    p.drawString(15*mm, height - 47*mm, f"Fournisseur : {commande.fournisseur.nom}")

    y = height - 60*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Médicament")
    p.drawString(80*mm, y, "Qté attendue")
    p.drawString(120*mm, y, "Qté reçue")
    p.drawString(155*mm, y, "Statut")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    for ligne in commande.lignes.all():
        y -= 7*mm
        p.drawString(15*mm, y, ligne.medicament.nom_commercial[:35])
        p.drawString(80*mm, y, str(ligne.quantite_commandee))
        p.drawString(120*mm, y, str(ligne.quantite_recue))
        if ligne.reste_a_recevoir == 0:
            p.drawString(155*mm, y, "Complet")
        else:
            p.drawString(155*mm, y, f"Manque {ligne.reste_a_recevoir}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer