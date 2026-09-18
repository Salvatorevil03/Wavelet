import argparse
import json
import os
from pathlib import Path

from .agent import AgentError, SCHEMA, compile_policy, make_payload
from .catalog import SOURCE, TAGS, VERSION


def main():
    parser = argparse.ArgumentParser(description='Win4Win: policy aziendali → regole per Rizzo PII')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('tags', help='Mostra il catalogo dei 22 tag')
    commands.add_parser('schema', help='Mostra lo schema di output richiesto all’agente')
    analyze = commands.add_parser('analyze', help='Invia le policy all’API e genera una bozza')
    analyze.add_argument('policies', nargs='+', type=Path)
    analyze.add_argument('--destination', required=True)
    analyze.add_argument('--purpose', required=True)
    analyze.add_argument('--model', default=os.environ.get('GEMINI_MODEL'))
    analyze.add_argument('--output', type=Path, required=True)
    analyze.add_argument('--dry-run', action='store_true', help='Controlla input senza chiamare API')
    args = parser.parse_args()
    try:
        if args.command == 'tags':
            print(json.dumps({'version': VERSION, 'source': SOURCE, 'tags': TAGS}, ensure_ascii=False, indent=2))
        elif args.command == 'schema':
            print(json.dumps(SCHEMA, indent=2))
        else:
            if args.output.exists():
                raise AgentError('Output già presente: scegliere un nuovo percorso')
            if not args.output.parent.is_dir():
                raise AgentError('La cartella di output non esiste')
            documents = []
            for i, path in enumerate(args.policies):
                if path.suffix.lower() not in {'.txt', '.md'}:
                    raise AgentError('Supportati soltanto file UTF-8 .txt e .md')
                if path.stat().st_size > 400_000:
                    raise AgentError('File troppo grande')
                documents.append({'id': f'policy_{i + 1}', 'text': path.read_text(encoding='utf-8')})
            if not args.model:
                raise AgentError('Specificare --model o GEMINI_MODEL')
            make_payload(documents, args.destination, args.purpose, args.model)
            if args.dry_run:
                print(f'Input valido: {len(documents)} documenti, 22 tag. Nessuna chiamata API.')
                return
            result = compile_policy(documents, args.destination, args.purpose, args.model)
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
            print('Bozza salvata. Le citazioni possono contenere informazioni riservate.')
    except (AgentError, OSError, UnicodeError) as exc:
        parser.exit(2, f'Errore: {exc}\n')


if __name__ == '__main__':
    main()
