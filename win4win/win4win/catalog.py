SOURCE = 'https://github.com/Rizzo-AI-Academy/rizzo-pii/blob/main/docs/TASSONOMIA_TAG.md'
VERSION = 'rizzo-22-observed-2026-09-18'
# Catalogo delle categorie, non delle etichette BIO. URL è solo regex nell'app.
TAGS = {
    'FULLNAME': 'Nome di persona; non distingue cliente, dipendente o ruolo legale',
    'AGE': 'Età', 'GENDER': 'Sesso o genere', 'DATE': 'Data di calendario',
    'TIME': 'Orario', 'STREET': 'Via o piazza', 'BUILDINGNUM': 'Numero civico',
    'ZIPCODE': 'Codice postale', 'CITY': 'Città', 'PROVINCE': 'Sigla provincia',
    'EMAIL': 'Indirizzo email o PEC', 'TELEPHONENUM': 'Numero di telefono',
    'CF': 'Codice fiscale', 'PIVA': 'Partita IVA',
    'ID_DOC': 'Numero di documento personale', 'IBAN': 'IBAN o numero di conto',
    'CREDITCARDNUMBER': 'Numero carta di credito', 'AMOUNT': 'Importo monetario',
    'TARGA': 'Targa veicolo', 'ORG': 'Organizzazione privata o ragione sociale',
    'DOCID': 'Identificativo di atto, procedura o rapporto',
    'CATASTO': 'Riferimenti catastali',
}
