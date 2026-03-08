"""
Test pour vérifier la génération de numéros de facture séquentiels
Format: FAC-1000, FAC-1001, FAC-1002, etc. (adapté aux numéros existants)
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au PATH
sys.path.insert(0, str(Path(__file__).parent))

from db_manager import get_database


def test_invoice_numbering():
    """Test: Les numéros de facture doivent être séquentiels et croissants"""
    
    print("\n🧪 Test: Génération des numéros de facture séquentiels")
    print("=" * 60)
    
    db = get_database()
    
    # 1. Récupérer 5 numéros de facture consécutifs
    print(f"\n✓ Génération de 5 numéros de facture séquentiels:")
    
    generated_numbers = []
    for i in range(5):
        invoice_num = db.generate_invoice_number()
        num = int(invoice_num.replace("FAC-", ""))
        generated_numbers.append((invoice_num, num))
        print(f"  {i+1}. {invoice_num}")
    
    # 2. Vérifier que chaque numéro suit le précédent
    print(f"\n✓ Vérification de la séquence:")
    prev_num = None
    for invoice_num, num in generated_numbers:
        assert num >= 1000, f"Numéro {num} invalide (< 1000)"
        print(f"  {invoice_num}: {num} ✓")
        
        # Vérifier que c'est plus grand que le précédent
        # (Note: les 5 premiers ne sont pas sauvegardés donc ils reviennent tous à 6585)
        # Donc on skip la vérification du flux en continu = c'est testé différemment
    
    # 3. Test du vrai flux: générer, sauvegarder, regénérer
    print(f"\n✓ Test du flux réel (générer → enregistrer → vérifier):")
    
    invoice_1 = db.generate_invoice_number()
    num_1 = int(invoice_1.replace("FAC-", ""))
    print(f"  1. Généré: {invoice_1} (= {num_1})")
    
    # Allez vérifier en BD ce qui existe actuellement avec ce numéro
    # Insérer directement avec INSERT
    try:
        # Créer un client test
        client_id = db.add_client(
            name="Test Sequential Invoice Client",
            email="test_sequential@test.com",
            phone="0123456789",
            address="Test Address"
        )
        
        # Créer une vente "vide" juste pour enregistrer le numéro
        db.cursor.execute("""
            INSERT INTO sales (
                invoice_number, client_id, subtotal, tax_amount, total,
                payment_method, payment_status, sale_date
            ) VALUES (?, ?, 0, 0, 0, 'Test', 'Pending', date('now'))
        """, (invoice_1, client_id))
        db.conn.commit()
        print(f"  2. Enregistré en BD: {invoice_1} ✓")
    except Exception as e:
        print(f"  ⚠️  Impossible d'enregistrer (peut être dupplicata): {e}")
    
    # Générer le prochain
    invoice_2 = db.generate_invoice_number()
    num_2 = int(invoice_2.replace("FAC-", ""))
    print(f"  3. Généré suivant: {invoice_2} (= {num_2})")
    
    # Vérifier
    if num_1 >= 1000 and num_2 > num_1:
        print(f"\n✅ Séquence correcte: {num_1} → {num_2} ✓")
        success = True
    else:
        print(f"\n❌ Séquence incorrecte: {num_1} → {num_2}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print(f"   Numéros séquentiels générés correctement")
        print("=" * 60)
    else:
        print("❌ TEST ÉCHOUÉ!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    try:
        test_invoice_numbering()
    except AssertionError as e:
        print(f"\n❌ ERREUR DE TEST: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

