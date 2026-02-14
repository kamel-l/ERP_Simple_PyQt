"""
Module d'envoi de factures par email
Envoie des factures PDF par email avec template HTML professionnel
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailSender:
    """Classe pour envoyer des emails avec pièces jointes"""
    
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialise le client email
        
        Args:
            smtp_server: Serveur SMTP (ex: smtp.gmail.com)
            smtp_port: Port SMTP (ex: 587 pour TLS)
            sender_email: Email de l'expéditeur
            sender_password: Mot de passe de l'expéditeur
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_invoice(self, recipient_email, invoice_number, pdf_path, 
                     customer_name="Client", company_name="Ma Société"):
        """
        Envoie une facture par email
        
        Args:
            recipient_email: Email du destinataire
            invoice_number: Numéro de facture
            pdf_path: Chemin vers le fichier PDF
            customer_name: Nom du client
            company_name: Nom de l'entreprise
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        
        try:
            # Créer le message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = f"Facture {invoice_number} - {company_name}"
            
            # Corps du message en HTML
            html_body = self._create_email_body(
                invoice_number, 
                customer_name, 
                company_name
            )
            
            message.attach(MIMEText(html_body, 'html'))
            
            # Attacher le PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(pdf_path)}'
                    )
                    message.attach(part)
            else:
                print(f"⚠️ Fichier PDF non trouvé: {pdf_path}")
                return False
            
            # Connexion au serveur SMTP et envoi
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Sécuriser la connexion
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Email envoyé à {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {str(e)}")
            return False
    
    def _create_email_body(self, invoice_number, customer_name, company_name):
        """Crée le corps HTML de l'email"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0A84FF 0%, #5E5CE6 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 25px;
                    border-radius: 10px;
                    border-left: 4px solid #0A84FF;
                }}
                .invoice-number {{
                    background: #0A84FF;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    display: inline-block;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .info-box {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #eee;
                    color: #666;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background: #30D158;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .warning {{
                    background: #FFF3CD;
                    border-left: 4px solid #FFD60A;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📄 {company_name}</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Facture électronique</p>
            </div>
            
            <div class="content">
                <h2>Bonjour {customer_name},</h2>
                
                <p>Veuillez trouver ci-joint votre facture :</p>
                
                <div style="text-align: center;">
                    <div class="invoice-number">
                        📋 Facture N° {invoice_number}
                    </div>
                </div>
                
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #0A84FF;">📎 Document joint</h3>
                    <p>✅ Facture au format PDF</p>
                    <p style="color: #666; font-size: 14px;">
                        Le document PDF joint contient tous les détails de votre commande.
                    </p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important :</strong><br>
                    Merci de vérifier les informations de la facture. En cas d'erreur, 
                    veuillez nous contacter dans les plus brefs délais.
                </div>
                
                <p>Pour toute question concernant cette facture, n'hésitez pas à nous contacter.</p>
                
                <div style="text-align: center;">
                    <a href="mailto:{self.sender_email}" class="button">
                        💬 Nous contacter
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>{company_name}</strong></p>
                <p>Email: {self.sender_email}</p>
                <p style="font-size: 12px; color: #999; margin-top: 15px;">
                    Cet email et ses pièces jointes sont confidentiels.<br>
                    Si vous avez reçu cet email par erreur, merci de le supprimer.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html


class EmailConfig:
    """Configuration email pour différents fournisseurs"""
    
    # Configurations pré-définies
    GMAIL = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587
    }
    
    OUTLOOK = {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587
    }
    
    YAHOO = {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587
    }
    
    @staticmethod
    def get_sender(provider='gmail', email='', password=''):
        """
        Crée un EmailSender avec la configuration du fournisseur
        
        Args:
            provider: 'gmail', 'outlook', ou 'yahoo'
            email: Adresse email
            password: Mot de passe (ou mot de passe d'application)
            
        Returns:
            Instance de EmailSender
        """
        configs = {
            'gmail': EmailConfig.GMAIL,
            'outlook': EmailConfig.OUTLOOK,
            'yahoo': EmailConfig.YAHOO
        }
        
        config = configs.get(provider.lower(), EmailConfig.GMAIL)
        
        return EmailSender(
            smtp_server=config['smtp_server'],
            smtp_port=config['smtp_port'],
            sender_email=email,
            sender_password=password
        )


def send_invoice_email(recipient_email, invoice_number, pdf_path,
                      sender_config, customer_name="Client", 
                      company_name="Ma Société"):
    """
    Fonction utilitaire pour envoyer rapidement une facture
    
    Args:
        recipient_email: Email du destinataire
        invoice_number: Numéro de facture
        pdf_path: Chemin vers le PDF
        sender_config: Dict avec 'email', 'password', 'provider'
        customer_name: Nom du client
        company_name: Nom de l'entreprise
        
    Returns:
        True si envoyé, False sinon
    """
    
    sender = EmailConfig.get_sender(
        provider=sender_config.get('provider', 'gmail'),
        email=sender_config['email'],
        password=sender_config['password']
    )
    
    return sender.send_invoice(
        recipient_email=recipient_email,
        invoice_number=invoice_number,
        pdf_path=pdf_path,
        customer_name=customer_name,
        company_name=company_name
    )


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de l'expéditeur
    sender_config = {
        'provider': 'gmail',
        'email': 'votre.email@gmail.com',
        'password': 'votre_mot_de_passe_application'  # Mot de passe d'application Google
    }
    
    # Envoyer la facture
    success = send_invoice_email(
        recipient_email='client@example.com',
        invoice_number='FAC-2026-001',
        pdf_path='facture.pdf',
        sender_config=sender_config,
        customer_name='Entreprise X',
        company_name='Ma Société SARL'
    )
    
    if success:
        print("✅ Facture envoyée avec succès !")
    else:
        print("❌ Échec de l'envoi")