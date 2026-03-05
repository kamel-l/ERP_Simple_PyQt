"""
Module de génération de factures PDF
Design style DAR ELSSALEM — bandes bleues marines, tableau professionnel
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime


# ─────────────────────────────────────────────────────────────
#  Palette couleurs (style DAR ELSSALEM)
# ─────────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor('#1E3A5F')   # bleu marine principal
C_GOLD   = colors.HexColor('#C9A84C')   # or du logo
C_WHITE  = colors.white
C_LIGHT  = colors.HexColor('#F5F7FA')   # gris très clair (lignes alternées)
C_BORDER = colors.HexColor('#D1D9E6')   # bordures tableau
C_TEXT   = colors.HexColor('#1A1A2E')   # texte principal
C_MUTED  = colors.HexColor('#6B7280')   # texte secondaire


# ─────────────────────────────────────────────────────────────
#  Utilitaires de conversion sécurisée
# ─────────────────────────────────────────────────────────────
def _f(val, default=0.0):
    """Float sécurisé — jamais de crash si val est None ou ''."""
    try:
        return float(val or default)
    except (ValueError, TypeError):
        return default

def _i(val, default=0):
    """Int sécurisé."""
    try:
        return int(val or default)
    except (ValueError, TypeError):
        return default

def _s(val, default=''):
    """Str sécurisé."""
    if val is None:
        return default
    s = str(val).strip()
    return s if s else default


# ─────────────────────────────────────────────────────────────
#  Classe principale
# ─────────────────────────────────────────────────────────────
class InvoicePDF:
    """Génère une facture PDF au format professionnel DAR ELSSALEM."""

    def __init__(self, filename="facture.pdf"):
        self.filename = filename

    def generate(self, invoice_data):
        """
        Génère le PDF et retourne le chemin du fichier.

        Clés attendues dans invoice_data :
            invoice_number, date,
            company  : {name, address, phone, email, nif, nis, rc}
            customer : {name, address, phone}
            items    : [{product, reference, quantity, price, discount, total}]
            subtotal, tax, tax_rate, total
        """
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=1.8*cm, leftMargin=1.8*cm,
            topMargin=1.5*cm,   bottomMargin=1.5*cm,
        )

        styles = getSampleStyleSheet()

        # ── Styles typographiques ─────────────────────────────
        def ps(name, **kw):
            return ParagraphStyle(name, parent=styles['Normal'], **kw)

        sty_inv_title  = ps('InvTitle',  fontSize=26, fontName='Helvetica-Bold',
                             textColor=C_TEXT, alignment=TA_RIGHT)
        sty_co_name    = ps('CoName',    fontSize=12, fontName='Helvetica-Bold',
                             textColor=C_TEXT)
        sty_co_info    = ps('CoInfo',    fontSize=8.5, textColor=C_MUTED, leading=13)
        sty_meta_lbl   = ps('MetaLbl',   fontSize=9,  textColor=C_MUTED, alignment=TA_LEFT)
        sty_meta_val   = ps('MetaVal',   fontSize=9,  fontName='Helvetica-Bold',
                             textColor=C_TEXT, alignment=TA_RIGHT)
        sty_bill_tag   = ps('BillTag',   fontSize=8.5, textColor=C_MUTED)
        sty_bill_name  = ps('BillName',  fontSize=12, fontName='Helvetica-Bold',
                             textColor=C_TEXT)
        sty_bill_info  = ps('BillInfo',  fontSize=9,  textColor=C_MUTED, leading=13)
        sty_total_lbl  = ps('TotLbl',    fontSize=9.5, textColor=C_MUTED,  alignment=TA_RIGHT)
        sty_total_val  = ps('TotVal',    fontSize=9.5, fontName='Helvetica-Bold',
                             textColor=C_TEXT, alignment=TA_RIGHT)
        sty_grand_lbl  = ps('GrandLbl',  fontSize=12, fontName='Helvetica-Bold',
                             textColor=C_WHITE, alignment=TA_RIGHT)
        sty_grand_val  = ps('GrandVal',  fontSize=14, fontName='Helvetica-Bold',
                             textColor=C_WHITE, alignment=TA_RIGHT)
        sty_note       = ps('Note',      fontSize=9,  textColor=C_MUTED, alignment=TA_CENTER)
        sty_badge      = ps('Badge',     fontSize=16, fontName='Helvetica-Bold',
                             textColor=C_GOLD, alignment=TA_CENTER)

        # ── Récupération des données ──────────────────────────
        company  = invoice_data.get('company',  {}) or {}
        customer = invoice_data.get('customer', {}) or {}
        items    = invoice_data.get('items',    []) or []

        inv_num  = _s(invoice_data.get('invoice_number'), '—')
        inv_date = _s(invoice_data.get('date'), datetime.now().strftime('%d/%m/%Y'))
        subtotal = _f(invoice_data.get('subtotal'))
        tax_amt  = _f(invoice_data.get('tax'))
        tax_rate = _f(invoice_data.get('tax_rate', 19))
        total    = _f(invoice_data.get('total'))

        co_name  = _s(company.get('name'),    'Ma Société')
        co_addr  = _s(company.get('address'))
        co_phone = _s(company.get('phone'))
        co_email = _s(company.get('email'))
        co_nif   = _s(company.get('nif'))
        co_nis   = _s(company.get('nis'))
        co_rc    = _s(company.get('rc'))

        cl_name  = _s(customer.get('name'),    'Client Anonyme')
        cl_addr  = _s(customer.get('address'))
        cl_phone = _s(customer.get('phone'))

        elements = []

        # ─────────────────────────────────────────────────────
        #  1. BANDE BLEUE SUPÉRIEURE
        # ─────────────────────────────────────────────────────
        elements.append(HRFlowable(
            width="100%", thickness=12,
            color=C_NAVY, spaceAfter=18
        ))

        # ─────────────────────────────────────────────────────
        #  2. EN-TÊTE : badge société (gauche) + FACTURE (droite)
        # ─────────────────────────────────────────────────────
        initials = co_name[:3].upper()
        badge_inner = Table(
            [[Paragraph(initials, sty_badge)]],
            colWidths=[2*cm], rowHeights=[2*cm]
        )
        badge_inner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_NAVY),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ('BOX',        (0,0), (-1,-1), 1.5, C_GOLD),
            ('ROUNDEDCORNERS', [6]),
        ]))

        # Infos société sous le badge
        co_paras = [badge_inner, Spacer(0, 0.25*cm),
                    Paragraph(co_name.upper(), sty_co_name)]
        if co_addr:  co_paras.append(Paragraph(co_addr, sty_co_info))
        if co_phone: co_paras.append(Paragraph(f"Tél : {co_phone}", sty_co_info))
        if co_email: co_paras.append(Paragraph(f"Email : {co_email}", sty_co_info))
        if co_nif:   co_paras.append(Paragraph(f"NIF : {co_nif}", sty_co_info))
        if co_nis:   co_paras.append(Paragraph(f"NIS : {co_nis}", sty_co_info))
        if co_rc:    co_paras.append(Paragraph(f"RC : {co_rc}", sty_co_info))

        # Bloc droit : titre + méta
        meta_rows = [
            [Paragraph("Date :",       sty_meta_lbl), Paragraph(inv_date, sty_meta_val)],
            [Paragraph("N° Facture :", sty_meta_lbl), Paragraph(inv_num,  sty_meta_val)],
        ]
        meta_tbl = Table(meta_rows, colWidths=[3*cm, 5*cm])
        meta_tbl.setStyle(TableStyle([
            ('ALIGN',         (0,0), (0,-1), 'LEFT'),
            ('ALIGN',         (1,0), (1,-1), 'RIGHT'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING',    (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        right_block = [
            Paragraph("FACTURE", sty_inv_title),
            Spacer(0, 0.2*cm),
            HRFlowable(width="100%", thickness=0.8, color=C_NAVY, spaceAfter=6),
            meta_tbl,
        ]

        header_tbl = Table(
            [[co_paras, right_block]],
            colWidths=[9*cm, 8.5*cm]
        )
        header_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(header_tbl)
        elements.append(Spacer(0, 0.4*cm))

        # ─────────────────────────────────────────────────────
        #  3. BANDE DORÉE
        # ─────────────────────────────────────────────────────
        elements.append(HRFlowable(
            width="100%", thickness=5,
            color=C_GOLD, spaceAfter=14
        ))

        # ─────────────────────────────────────────────────────
        #  4. SECTION "FACTURÉ À"
        # ─────────────────────────────────────────────────────
        bill_block = [
            Paragraph("Facturé à :", sty_bill_tag),
            Paragraph(cl_name.upper(), sty_bill_name),
        ]
        if cl_addr:  bill_block.append(Paragraph(cl_addr,          sty_bill_info))
        if cl_phone: bill_block.append(Paragraph(f"Tél : {cl_phone}", sty_bill_info))

        bill_tbl = Table([[bill_block]], colWidths=[17.5*cm])
        bill_tbl.setStyle(TableStyle([
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(bill_tbl)
        elements.append(Spacer(0, 0.5*cm))

        # ─────────────────────────────────────────────────────
        #  5. TABLEAU DES ARTICLES
        # ─────────────────────────────────────────────────────
        col_headers = ['Qté', 'Référence', 'Description', 'Prix Unit.', 'TVA %', 'Total']
        table_data  = [col_headers]

        for item in items:
            qty      = _i(item.get('quantity'))
            ref      = _s(item.get('reference'), '—')
            product  = _s(item.get('product'),   'N/A')
            price    = _f(item.get('price'))
            discount = _f(item.get('discount'))
            itotal   = _f(item.get('total'))

            # Remise : si > 0, on l'affiche, sinon on met le taux TVA
            if discount > 0:
                tva_cell = f"Remise {discount:.1f}%"
            else:
                tva_cell = f"{tax_rate:.0f}%"

            table_data.append([
                str(qty),
                ref,
                product,
                f"{price:,.2f} DA",
                tva_cell,
                f"{itotal:,.2f} DA",
            ])

        col_w     = [1.4*cm, 2.8*cm, 6.3*cm, 2.5*cm, 1.8*cm, 2.7*cm]
        items_tbl = Table(table_data, colWidths=col_w, repeatRows=1)

        # Zèbrage des lignes
        n = len(table_data)
        row_bgs = [
            ('BACKGROUND', (0, i), (-1, i), C_WHITE if i % 2 == 1 else C_LIGHT)
            for i in range(1, n)
        ]

        items_tbl.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND',    (0, 0), (-1, 0), C_NAVY),
            ('TEXTCOLOR',     (0, 0), (-1, 0), C_WHITE),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 9),
            ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 9),
            # Corps
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('TEXTCOLOR',     (0, 1), (-1, -1), C_TEXT),
            ('ALIGN',         (0, 1), (0, -1), 'CENTER'),   # Qté
            ('ALIGN',         (1, 1), (1, -1), 'CENTER'),   # Ref
            ('ALIGN',         (2, 1), (2, -1), 'LEFT'),     # Description
            ('ALIGN',         (3, 1), (3, -1), 'RIGHT'),    # Prix
            ('ALIGN',         (4, 1), (4, -1), 'CENTER'),   # TVA
            ('ALIGN',         (5, 1), (5, -1), 'RIGHT'),    # Total
            ('FONTNAME',      (5, 1), (5, -1), 'Helvetica-Bold'),
            ('TOPPADDING',    (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            # Bordures
            ('BOX',       (0, 0), (-1, -1), 1,   C_BORDER),
            ('LINEBELOW', (0, 0), (-1, 0),   1.5, C_NAVY),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, C_BORDER),
            *row_bgs,
        ]))
        elements.append(items_tbl)
        elements.append(Spacer(0, 0.7*cm))

        # ─────────────────────────────────────────────────────
        #  6. TOTAUX
        # ─────────────────────────────────────────────────────
        totals_rows = [
            [Paragraph("Sous-total HT :", sty_total_lbl),
             Paragraph(f"{subtotal:,.2f} DA", sty_total_val)],
            [Paragraph(f"TVA ({tax_rate:.0f}%) :", sty_total_lbl),
             Paragraph(f"{tax_amt:,.2f} DA", sty_total_val)],
        ]
        totals_tbl = Table(totals_rows, colWidths=[13.5*cm, 4*cm])
        totals_tbl.setStyle(TableStyle([
            ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(totals_tbl)
        elements.append(Spacer(0, 0.25*cm))

        elements.append(HRFlowable(
            width="100%", thickness=1,
            color=C_BORDER, spaceAfter=8
        ))

        # Ligne TOTAL TTC — fond bleu marine
        grand_tbl = Table(
            [[Paragraph("TOTAL TTC :", sty_grand_lbl),
              Paragraph(f"{total:,.2f} DA", sty_grand_val)]],
            colWidths=[13.5*cm, 4*cm]
        )
        grand_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), C_NAVY),
            ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING',    (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING',   (0,0), (-1,-1), 12),
            ('RIGHTPADDING',  (0,0), (-1,-1), 12),
            ('ROUNDEDCORNERS', [4]),
        ]))
        elements.append(grand_tbl)
        elements.append(Spacer(0, 1.2*cm))

        # ─────────────────────────────────────────────────────
        #  7. NOTES DE BAS DE PAGE
        # ─────────────────────────────────────────────────────
        for note in [
            "Veuillez nous contacter pour plus d'informations sur les options de paiement.",
            "Nous vous remercions de votre confiance.",
        ]:
            elements.append(Paragraph(f"<b>{note}</b>", sty_note))
            elements.append(Spacer(0, 0.12*cm))

        elements.append(Spacer(0, 0.6*cm))

        # ─────────────────────────────────────────────────────
        #  8. BANDE BLEUE INFÉRIEURE
        # ─────────────────────────────────────────────────────
        elements.append(HRFlowable(
            width="100%", thickness=12,
            color=C_NAVY, spaceBefore=4
        ))

        # ── Build ─────────────────────────────────────────────
        doc.build(elements)
        return self.filename


# ─────────────────────────────────────────────────────────────
#  Fonction utilitaire (interface publique)
# ─────────────────────────────────────────────────────────────
def create_invoice_pdf(invoice_data, filename="facture.pdf"):
    """
    Crée une facture PDF et retourne le chemin du fichier.

    Args:
        invoice_data : dict avec les données de la facture
        filename     : chemin complet du fichier PDF à générer

    Returns:
        Chemin absolu du fichier PDF créé
    """
    pdf = InvoicePDF(filename)
    return pdf.generate(invoice_data)


# ─────────────────────────────────────────────────────────────
#  Test autonome
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        'invoice_number': 'FAC-2026-001',
        'date':           datetime.now().strftime('%d/%m/%Y'),
        'company': {
            'name':    'DAR ELSSALEM SARL',
            'address': '123 Rue Example, Alger 16000',
            'phone':   '023 45 67 89',
            'email':   'contact@darelssalem.dz',
            'nif':     '123456789012345',
            'nis':     '123456789012',
            'rc':      '12/34567890',
        },
        'customer': {
            'name':    'ABD ALMALEK',
            'address': 'BORJMNAYEL',
            'phone':   '0555 12 34 56',
        },
        'items': [
            {'product': 'FEUILLE CHINE', 'reference': '106801',
             'quantity': 510, 'price': 150.0, 'discount': None, 'total': 76500.0},
            {'product': 'FEUILLE CHINE', 'reference': '106798',
             'quantity': 518, 'price': 150.0, 'discount': 0,    'total': 77700.0},
            {'product': 'FEUILLE CHINE', 'reference': '106800',
             'quantity': 520, 'price': 150.0, 'discount': 0,    'total': 78000.0},
        ],
        'subtotal':  232200.0,
        'tax':       44118.0,
        'tax_rate':  19,
        'total':     276318.0,
    }

    out = create_invoice_pdf(sample, "/home/claude/facture_test.pdf")
    print(f"✅ PDF généré : {out}")