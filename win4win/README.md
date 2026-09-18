# Win4Win — agente policy

Prototipo Python che traduce policy aziendali in **bozze JSON** applicabili al
catalogo di Rizzo PII. Nessuna dipendenza esterna, Python 3.10 o successivo.
Non scarica né addestra BERT. Non modifica documenti operativi e non autorizza invii.

## Avvio

Aprire un terminale nella cartella del progetto:

```sh
python3 -m win4win tags
python3 -m win4win schema
python3 -m unittest discover -s tests -v
```

Configurare `GEMINI_API_KEY` in modo sicuro nell'ambiente del terminale; non inserirla
nei file del progetto. `.env` non viene caricato automaticamente. Impostare
`GEMINI_MODEL` oppure passare `--model` con un modello del proprio account che
supporti generateContent e output JSON strutturati. Non è fissato un modello a pagamento.

Controllo locale senza API (sostituire il nome modello per una chiamata reale):

```sh
python3 -m win4win analyze examples/policy.md \
  --destination "Servizio AI aziendale approvato" \
  --purpose "Revisione linguistica" \
  --model gemini-MODELLO_DEL_TUO_ACCOUNT \
  --output bozza.json --dry-run
```

Togliere `--dry-run` per eseguire la richiesta API. Il comando **invia integralmente
le policy e il contesto forniti a Google Gemini**: usare policy ammesse al servizio scelto.
L’uso e la conservazione dei dati dipendono dalle condizioni del servizio Google
utilizzato; questa integrazione non garantisce zero retention o conformità. La chiamata può comportare costi API.
Non vengono letti automaticamente altri file né documenti da anonimizzare.

Supportati uno o più file UTF-8 `.txt` / `.md`; PDF e DOCX vanno prima convertiti e
controllati. Limite complessivo 100.000 caratteri, senza troncamento silenzioso.
La corrispondenza source_id segue l'ordine degli argomenti: policy_1, policy_2, ecc.

## Contratto dell'output

- Una regola per ogni tag: `allow`, `replace`, `redact`, `block`, `review`.
- `replace`: futuro segnaposto stabile; `redact`: futura rimozione dello span;
  `block`: bloccare l'esportazione se il tag viene rilevato. Qui sono solo proposte.
- Condizioni non verificate e categorie non disciplinate: `review`.
- `unmapped_requirements`: requisiti che i tag non coprono; non ignorarli a valle.
- Evidenze: identificativo fonte e citazione letterale verificata nel file.
- Hash SHA-256 dei testi sorgente, contesto destinazione/finalità, versione catalogo.
- Sempre `status: draft`, `requires_human_review: true`, `automatic_export_enabled: false`.

Il controllo delle citazioni ne verifica l'esistenza, **non** che giustifichino
semanticamente l'azione: è necessaria verifica della bozza. Il prompt separa i
documenti dalle istruzioni, ma non garantisce resistenza assoluta a prompt injection.
Test automatici coprono il contratto e i fallimenti; non sostituiscono una valutazione
del modello su policy reali e avversariali. Errori API, output incompleti o invalidi
non producono una policy. L'output non sovrascrive file esistenti ed è creato con
permessi 0600: contiene estratti potenzialmente riservati delle policy.

## Catalogo verificato

22 categorie del modello, rilevate il 18 settembre 2026 dalla
[tassonomia ufficiale](https://github.com/Rizzo-AI-Academy/rizzo-pii/blob/main/docs/TASSONOMIA_TAG.md).
`URL` è escluso: il progetto originale lo rileva tramite regex, non tramite BERT.
`B-` e `I-` sono prefissi BIO; `O` non è una categoria da configurare.
La documentazione upstream contiene una riga finale che menziona 23 tag, ma tabella,
introduzione e nota su URL distinguono esplicitamente 22 categorie del modello.
Il catalogo è uno snapshot locale, non si aggiorna durante le esecuzioni. Prima
dell'integrazione con un checkpoint verificare il suo `id2label` contro il catalogo.

Il catalogo non copre tutti i dati personali o tutte le informazioni riservate:
salute, credenziali, ruoli cliente/dipendente e strategie commerciali non sono
categorie dedicate. Il comportamento del modello non stabilisce la qualificazione
giuridica dei dati. Questo agente non ricerca norme né certifica GDPR/AI Act:
traduce documenti forniti e segnala lacune da risolvere con i responsabili della policy.

## Passo successivo

Validare le bozze e realizzare separatamente il motore Python che applica regole
approvate agli span del modello. Nessun motore di sostituzione è incluso in questa
prima versione dell'agente. Il modello Rizzo e l'eventuale fine-tuning restano separati.

Integrazione API basata sulla [documentazione ufficiale Google Gemini](https://ai.google.dev/api/generate-content).
