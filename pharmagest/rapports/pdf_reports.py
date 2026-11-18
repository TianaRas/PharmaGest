import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

def generer_rapport_stock_pdf(lots):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(15*mm, height - 15*mm, "PHARMAGEST - Rapport de Stock")
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 22*mm, f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.line(15*mm, height - 26*mm, width - 15*mm, height - 26*mm)

    y = height - 35*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Médicament")
    p.drawString(70*mm, y, "N° Lot")
    p.drawString(105*mm, y, "Péremption")
    p.drawString(135*mm, y, "Quantité")
    p.drawString(160*mm, y, "Fournisseur")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    for lot in lots:
        y -= 7*mm
        if y < 20*mm:
            p.showPage()
            y = height - 20*mm
            p.setFont("Helvetica", 9)
        p.drawString(15*mm, y, lot.medicament.nom_commercial[:30])
        p.drawString(70*mm, y, lot.numero_lot)
        p.drawString(105*mm, y, lot.date_peremption.strftime('%d/%m/%Y'))
        p.drawString(135*mm, y, str(lot.quantite_actuelle))
        p.drawString(160*mm, y, lot.fournisseur.nom[:20] if lot.fournisseur else "-")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generer_rapport_ventes_pdf(ventes):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(15*mm, height - 15*mm, "PHARMAGEST - Rapport des Ventes")
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 22*mm, f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.line(15*mm, height - 26*mm, width - 15*mm, height - 26*mm)

    y = height - 35*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Référence")
    p.drawString(55*mm, y, "Date")
    p.drawString(95*mm, y, "Client")
    p.drawString(145*mm, y, "Total (Ar)")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    total_general = 0
    for vente in ventes:
        y -= 7*mm
        if y < 20*mm:
            p.showPage()
            y = height - 20*mm
            p.setFont("Helvetica", 9)
        p.drawString(15*mm, y, vente.reference)
        p.drawString(55*mm, y, vente.date_vente.strftime('%d/%m/%Y %H:%M'))
        p.drawString(95*mm, y, vente.client.nom[:30] if vente.client else "Comptoir")
        p.drawString(145*mm, y, str(vente.total))
        total_general += vente.total

    y -= 10*mm
    p.line(15*mm, y, width - 15*mm, y)
    y -= 8*mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(120*mm, y, "TOTAL GÉNÉRAL :")
    p.drawString(155*mm, y, f"{total_general} Ar")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- NOUVEAUX RAPPORTS ---

def generer_rapport_achats_pdf(commandes):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(15*mm, height - 15*mm, "PHARMAGEST - Rapport des Achats")
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 22*mm, f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.line(15*mm, height - 26*mm, width - 15*mm, height - 26*mm)

    y = height - 35*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Référence")
    p.drawString(50*mm, y, "Date")
    p.drawString(80*mm, y, "Fournisseur")
    p.drawString(130*mm, y, "Statut")
    p.drawString(160*mm, y, "Total (Ar)")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    total_general = 0
    for commande in commandes:
        y -= 7*mm
        if y < 20*mm:
            p.showPage()
            y = height - 20*mm
            p.setFont("Helvetica", 9)
        p.drawString(15*mm, y, commande.reference)
        p.drawString(50*mm, y, commande.date_commande.strftime('%d/%m/%Y'))
        p.drawString(80*mm, y, commande.fournisseur.nom[:25])
        p.drawString(130*mm, y, commande.get_statut_display())
        p.drawString(160*mm, y, f"{commande.total_commande}")
        total_general += commande.total_commande

    y -= 10*mm
    p.line(15*mm, y, width - 15*mm, y)
    y -= 8*mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(120*mm, y, "TOTAL ACHATS :")
    p.drawString(155*mm, y, f"{total_general} Ar")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generer_rapport_peremptions_pdf(lots):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(15*mm, height - 15*mm, "PHARMAGEST - Produits proches de la péremption")
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 22*mm, f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(15*mm, height - 27*mm, "(Lots périmant dans les 30 prochains jours)")
    p.line(15*mm, height - 31*mm, width - 15*mm, height - 31*mm)

    y = height - 40*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Médicament")
    p.drawString(70*mm, y, "N° Lot")
    p.drawString(110*mm, y, "Péremption")
    p.drawString(150*mm, y, "Quantité")
    p.drawString(180*mm, y, "Jours restants")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)
    p.setFont("Helvetica", 9)

    aujourd_hui = timezone.now().date()

    for lot in lots:
        y -= 7*mm
        if y < 20*mm:
            p.showPage()
            y = height - 20*mm
            p.setFont("Helvetica", 9)
        
        jours_restants = (lot.date_peremption - aujourd_hui).days
        
        p.drawString(15*mm, y, lot.medicament.nom_commercial[:35])
        p.drawString(70*mm, y, lot.numero_lot)
        p.drawString(110*mm, y, lot.date_peremption.strftime('%d/%m/%Y'))
        p.drawString(150*mm, y, str(lot.quantite_actuelle))
        p.drawString(180*mm, y, str(jours_restants))

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer