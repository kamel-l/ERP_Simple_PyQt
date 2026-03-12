"""Debug: Vérifier les numéros de facture existants"""
from db_manager import get_database

db = get_database()
db.cursor.execute('SELECT invoice_number FROM sales WHERE invoice_number LIKE "FAC-%" ORDER BY invoice_number DESC LIMIT 10')
results = db.cursor.fetchall()

print('\n📋 Derniers 10 numéros de facture en base:')
for i, r in enumerate(results, 1):
    inv_num = r['invoice_number']
    num_part = inv_num.replace("FAC-", "").strip()
    is_numeric = num_part.isdigit()
    print(f'{i}. {inv_num:25} → {num_part:20} (numeric: {is_numeric})')

print(f'\nTotal de factures: {len(results)}')

# Test la fonction
print('\n🧪 Test generate_invoice_number():')
next_inv = db.generate_invoice_number()
print(f'Prochain numéro: {next_inv}')
