"""
Module d'impression de factures en PDF
Génère des factures professionnelles avec logo et design moderne
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
import os


class InvoicePDF:
    """Classe pour générer des factures PDF professionnelles"""
    
    def __init__(self, filename="facture.pdf"):
        self.filename = filename
        self.width, self.height = A4
        
    def generate(self, invoice_data):
        """
        Génère la facture PDF
        
        invoice_data doit contenir:
        {
            'invoice_number': 'FAC-2026-001',
            'date': '14/02/2026',
            'company': {
                'name': 'Ma Société SARL',
                'address': '123 Rue Example, Alger',
                'phone': '023 45 67 89',
                'email': 'contact@masociete.dz',
                'nif': '123456789012345',
                'nis': '123456789012',
                'rc': '12/34567890'
            },
            'customer': {
                'name': 'Client Name',
                'address': 'Adresse client',
                'phone': '0555 12 34 56',
                'nif': '987654321098765' (optionnel)
            },
            'items': [
                {
                    'product': 'Nom produit',
                    'reference': 'REF-001',
                    'quantity': 2,
                    'price': 1500.00,
                    'discount': 10.0,
                    'total': 2700.00
                }
            ],
            'subtotal': 2700.00,
            'tax': 513.00,  # TVA 19%
            'total': 3213.00
        }
        """
        
        # Créer le document
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Conteneur pour les éléments
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0A84FF'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style pour les informations
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        # En-tête avec titre
        title = Paragraph("FACTURE", title_style)
        elements.append(title)
        
        # Informations facture et dates
        invoice_info = [
            [
                Paragraph(f"<b>N° Facture:</b> {invoice_data['invoice_number']}", info_style),
                Paragraph(f"<b>Date:</b> {invoice_data['date']}", info_style)
            ]
        ]
        
        info_table = Table(invoice_info, colWidths=[9*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Tableau avec infos entreprise et client
        company = invoice_data['company']
        customer = invoice_data['customer']
        
        company_text = f"""
        <b>{company['name']}</b><br/>
        {company['address']}<br/>
        Tél: {company['phone']}<br/>
        Email: {company['email']}<br/>
        NIF: {company.get('nif', 'N/A')}<br/>
        NIS: {company.get('nis', 'N/A')}<br/>
        RC: {company.get('rc', 'N/A')}
        """
        
        customer_text = f"""
        <b>FACTURER À:</b><br/>
        <b>{customer['name']}</b><br/>
        {customer.get('address', 'N/A')}<br/>
        Tél: {customer.get('phone', 'N/A')}
        """
        
        if customer.get('nif'):
            customer_text += f"<br/>NIF: {customer['nif']}"
        
        party_info = [
            [
                Paragraph(company_text, info_style),
                Paragraph(customer_text, info_style)
            ]
        ]
        
        party_table = Table(party_info, colWidths=[8.5*cm, 8.5*cm])
        party_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F0F0F0')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#E8F4FF')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(party_table)
        elements.append(Spacer(1, 1*cm))
        
        # Tableau des articles
        items_data = [
            ['Réf.', 'Désignation', 'Qté', 'P.U. (DA)', 'Remise', 'Total (DA)']
        ]
        
        for item in invoice_data['items']:
            items_data.append([
                item['reference'],
                item['product'],
                str(item['quantity']),
                f"{item['price']:,.2f}",
                f"{item['discount']}%" if item['discount'] > 0 else '-',
                f"{item['total']:,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[2.5*cm, 6*cm, 1.5*cm, 2.5*cm, 2*cm, 2.5*cm])
        items_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A84FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Référence
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),     # Désignation
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),   # Quantité
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),    # Prix
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),   # Remise
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),    # Total
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Lignes alternées
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            
            # Bordures
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0A84FF')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0A84FF')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 1*cm))
        
        # Tableau des totaux
        totals_data = [
            ['Sous-total HT:', f"{invoice_data['subtotal']:,.2f} DA"],
            ['TVA (19%):', f"{invoice_data['tax']:,.2f} DA"],
            ['', ''],  # Ligne vide pour séparation
            ['TOTAL TTC:', f"{invoice_data['total']:,.2f} DA"]
        ]
        
        totals_table = Table(totals_data, colWidths=[12*cm, 5*cm])
        totals_table.setStyle(TableStyle([
            # Lignes normales
            ('ALIGN', (0, 0), (0, 1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 1), 11),
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.HexColor('#333333')),
            ('TOPPADDING', (0, 0), (-1, 1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 1), 6),
            
            # Ligne totale
            ('ALIGN', (0, 3), (-1, 3), 'RIGHT'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#30D158')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F0F0F0')),
            ('TOPPADDING', (0, 3), (-1, 3), 12),
            ('BOTTOMPADDING', (0, 3), (-1, 3), 12),
            
            # Bordures
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#30D158')),
            ('BOX', (0, 3), (-1, 3), 1.5, colors.HexColor('#30D158')),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 1.5*cm))
        
        # Pied de page
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        footer_text = """
        <b>Conditions de paiement:</b> Paiement à réception de facture<br/>
        <i>Merci pour votre confiance !</i><br/>
        <br/>
        Cette facture est générée électroniquement et ne nécessite pas de signature.
        """
        
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
        
        # Générer le PDF
        doc.build(elements)
        
        return self.filename


def create_invoice_pdf(invoice_data, filename="facture.pdf"):
    """
    Fonction utilitaire pour créer rapidement une facture PDF
    
    Args:
        invoice_data: Dictionnaire contenant les données de la facture
        filename: Nom du fichier PDF à créer
        
    Returns:
        Chemin du fichier créé
    """
    pdf = InvoicePDF(filename)
    return pdf.generate(invoice_data)


# Exemple d'utilisation
if __name__ == "__main__":
    # Données exemple
    sample_invoice = {
        'invoice_number': 'FAC-2026-001',
        'date': datetime.now().strftime('%d/%m/%Y'),
        'company': {
            'name': 'Ma Société SARL',
            'address': '123 Rue Example, Alger 16000',
            'phone': '023 45 67 89',
            'email': 'contact@masociete.dz',
            'nif': '123456789012345',
            'nis': '123456789012',
            'rc': '12/34567890'
        },
        'customer': {
            'name': 'Entreprise X',
            'address': '456 Avenue Commerce, Oran',
            'phone': '0555 12 34 56',
            'nif': '987654321098765'
        },
        'items': [
            {
                'product': 'Ordinateur Portable HP ProBook',
                'reference': 'HP-001',
                'quantity': 5,
                'price': 75000.00,
                'discount': 10.0,
                'total': 337500.00
            },
            {
                'product': 'Souris Sans Fil Logitech',
                'reference': 'LOG-MS-100',
                'quantity': 10,
                'price': 1500.00,
                'discount': 0.0,
                'total': 15000.00
            }
        ],
        'subtotal': 352500.00,
        'tax': 66975.00,  # 19% TVA
        'total': 419475.00
    }
    
    # Créer la facture
    pdf_file = create_invoice_pdf(sample_invoice, "facture_exemple.pdf")
    print(f"✅ Facture créée: {pdf_file}")