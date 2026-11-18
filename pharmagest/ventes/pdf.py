import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors

def generer_recu_pdf(vente):
    # Créer un buffer (mémoire) pour stocker le PDF
    buffer = io.BytesIO()

    # Créer le canvas (format A5 pour un reçu)
    p = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    # --- En-tête (Pharmacie) ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(15*mm, height - 15*mm, "PHARMAGEST")
    
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 22*mm, "Votre pharmacie de confiance")
    p.drawString(15*mm, height - 27*mm, "Antananarivo, Madagascar")
    p.drawString(15*mm, height - 32*mm, "Tél: +261 34 00 000 00")

    # Ligne de séparation
    p.setStrokeColor(colors.black)
    p.line(15*mm, height - 36*mm, width - 15*mm, height - 36*mm)

    # --- Infos de la vente ---
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, height - 45*mm, f"Reçu N°: {vente.reference}")
    
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height - 50*mm, f"Date: {vente.date_vente.strftime('%d/%m/%Y %H:%M')}")
    
    client_nom = vente.client.nom if vente.client else "Client comptoir"
    p.drawString(15*mm, height - 55*mm, f"Client: {client_nom}")

    # --- Tableau des articles ---
    y = height - 70*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15*mm, y, "Article")
    p.drawString(width - 50*mm, y, "Qté")
    p.drawString(width - 35*mm, y, "Prix U.")
    p.drawString(width - 20*mm, y, "Total")

    y -= 5*mm
    p.line(15*mm, y, width - 15*mm, y)

    # Boucler sur les lignes de vente
    p.setFont("Helvetica", 9)
    for ligne in vente.lignes.all():
        y -= 8*mm
        p.drawString(15*mm, y, ligne.lot.medicament.nom_commercial[:25])
        p.drawString(width - 50*mm, y, str(ligne.quantite))
        p.drawString(width - 35*mm, y, f"{ligne.prix_unitaire} Ar")
        p.drawString(width - 20*mm, y, f"{ligne.sous_total} Ar")

    # --- Total ---
    y -= 10*mm
    p.line(15*mm, y, width - 15*mm, y)
    y -= 8*mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 50*mm, y, "TOTAL :")
    p.drawString(width - 25*mm, y, f"{vente.total} Ar")

    # --- Pied de page ---
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, 15*mm, "Merci de votre visite !")
    p.drawCentredString(width / 2, 10*mm, "Les médicaments ne sont ni repris ni échangés.")

    # Finaliser le PDF
    p.showPage()
    p.save()

    # Revenir au début du buffer pour pouvoir le lire
    buffer.seek(0)
    return buffer