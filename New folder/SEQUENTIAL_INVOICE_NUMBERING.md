## Sequential Invoice Numbering Implementation

**Date:** 2026-03-09
**Status:** ✅ Implemented and Tested

### Requirements Met
- ✅ Changed from timestamp-based invoice numbers (FAC-20260308143052) to sequential format (FAC-1000, FAC-1001, etc.)
- ✅ First invoice = 1000 (or continues from existing sequential numbers)
- ✅ Handles migration from old timestamp format gracefully
- ✅ Backward compatible with existing database

### Changes Made

#### 1. **db_manager.py** - New Method: `generate_invoice_number()`
Added at line ~400 (after `get_invoices_by_client()`)

```python
def generate_invoice_number(self):
    """
    Génère le prochain numéro de facture séquentiel
    Format: FAC-1000, FAC-1001, FAC-1002, etc.
    La première facture sera FAC-1000
    Gère la migration depuis ancien format FAC-timestamp
    
    Les nouveau format séquentiel: 1000-99999
    Les anciens timestamps (> 100000) sont ignorés
    """
```

**Key Features:**
- Queries all FAC-% invoice numbers from database
- Filters only sequential numbers (1000-99999 range)
- Ignores old timestamps (numbers > 100000)
- Returns FAC-{next_number} format
- Fallback to timestamp on error

#### 2. **sales.py** - Updated: `save_sale()` Method
**Location:** Line ~806-807

**Before:**
```python
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
invoice_number = f"FAC-{timestamp}"
```

**After:**
```python
# Générer un numéro de facture séquentiel (FAC-1000, FAC-1001, etc.)
invoice_number = self.db.generate_invoice_number()
```

### How It Works

1. When creating a sale in PointOfSale (`sales.py`):
   - Calls `self.db.generate_invoice_number()`
   - This queries the sales table for highest sequential invoice
   - Returns next sequential number (FAC-1000, FAC-1001, etc.)

2. Migration handling:
   - Old timestamp invoices (e.g., FAC-20260308143052) are recognized
   - System starts new sequential series at FAC-1000
   - Completely transparent to user

3. Range protection:
   - Sequential range: 1000-99999 (90,000 invoices max)
   - Numbers outside this range are treated as old format
   - Prevents old timestamps from interfering

### Test Results

**File:** `test_invoice_numbering.py`

```
✅ Test: Génération des numéros de facture séquentiels
✓ Génération de 5 numéros de facture séquentiels
✓ Vérification de la séquence
✓ Test du flux réel (générer → enregistrer → vérifier)
  1. Généré: FAC-6585 (= 6585)
  2. Enregistré en BD: FAC-6585 ✓
  3. Généré suivant: FAC-6586 (= 6586)
✅ Séquence correcte: 6585 → 6586 ✓
```

### Database Structure
- No schema changes required
- `sales.invoice_number` remains TEXT UNIQUE
- Migration from old format is automatic

### Integration Points
- ✅ **sales.py**: Uses new system in `save_sale()`
- ✅ **payment_module.py**: Receives invoice_number directly (no changes needed)
- ✅ **db_manager.py**: New `generate_invoice_number()` method
- ✅ **statistics_view.py**: Displays invoices (no changes needed)
- ✅ **advanced_analytics_view.py**: Views invoices (no changes needed)

### Backward Compatibility
- Existing invoices with timestamp format remain in database
- New invoices use sequential format
- System intelligently handles both formats
- No data migration required

### Example Usage Flow

```
First sale:
  1. Call generate_invoice_number() → 1000
  2. Show payment dialog with FAC-1000
  3. Save to database

Second sale:
  1. Call generate_invoice_number() → 1001
  2. Show payment dialog with FAC-1001
  3. Save to database

Old invoice lookup:
  1. Call generate_invoice_number()
  2. Database has FAC-20260308143052 (ignored)
  3. Returns next sequential: FAC-1002
```

### Performance Considerations
- Queries all FAC-% records (not optimal for large databases)
- Max invoice range: 90,000 (reasonable for most businesses)
- Could be optimized with `last_sequential_invoice` in settings table
- Current implementation is simple and reliable

### Future Enhancements
- [ ] Add settings table entry for next_invoice_number for faster lookup
- [ ] Add invoice number validation in UI
- [ ] Add invoice history/audit trail
- [ ] Support different numbering sequences per business unit

### Files Modified
1. `db_manager.py` - Added `generate_invoice_number()` method
2. `sales.py` - Updated invoice number generation in `save_sale()`
3. `test_invoice_numbering.py` - New test file (verification)
4. `debug_invoices.py` - Debug helper script

### Rollback Plan
If needed to revert:
1. Remove `generate_invoice_number()` from db_manager.py
2. Restore original lines in sales.py (lines 807-808)
3. Update any code referring to the new method
