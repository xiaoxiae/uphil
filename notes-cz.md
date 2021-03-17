# Notes
A collection of notes regarding the project(s), written in Czech.


## Jméno
- **Uphil** - Unorthodox Python Highlighter
- P(y)hil - Python Highlighter


## Typy highlightu
- proměnné podle datového typu
- proměnná se jménem stejným jako builtin
	- obarvit kolizi | barva proměnné, né builtinu
- rozlišovat importy z jiných zdrojáků vs. z aktuálního modulu
- barva podle stáří textu
- používání stejného jména proměnné

## Odkazy
- stránka LSP:     https://microsoft.github.io/language-server-protocol/
	- přehled:     https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/
	- specifikace: https://microsoft.github.io/language-server-protocol/specifications/specification-current/
		- document highlight: https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentHighlight
		- documet symbols:    https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentSymbol 


## Řešení

### První nápad

#### Server
- extension `pyls`u, který přečte to, co pyls k symbolům vymyslel, a přes `mypy` zjistí typy proměnných, funkcí a jiné havěti
	1. zkopíruje daný soubor a za místa symbolů přidá `reveal_type` direktivy
		- `pyls/hookspecs.py` specifikují to, co chceme
			- `pyls_document_highlight` -- možná chceme (je to hlavně k highlightování toho, na čem máme kurzor)
			- `pyls_document_symbols` -- určitě chceme, to jsou vysloveně symboly
	2. poštve na to `mypy` a zparsujeme message, které ke všem symbolům přidáme

#### Client
- extension (Neo)Vimu, která výsledek nějak rozumně zpracuje

---

## Diář

### 12. 3. 2021
- projetí toho, co to vlastně LSP je
- odkazy na části LSP webové stránky

### 13. 3. 2021
- pročítání protokolu
	- `Document Symbols Request`: https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentSymbol
		- určitě zvládne přenášet data o typu proměnné
		- `DocumentSymbol[]` - hierarchie symbolů; preferované
		- `SymbolInformation[]` - pouze list; nepreferované

### 14. 3. 2021
- procházení implementací rozšíření `pyls`
- hledání způsobu, jak zjišťovat data proměnných v `mypy`
	- někdo měl stejný problém: https://github.com/python/mypy/blob/master/mypy/api.py
	- dokumentace k `reveal_type`: https://mypy.readthedocs.io/en/latest/common_issues.html?highlight=reveal_type#reveal-type

### 15. 3. 2021
- nastavování `venv`u s `pyls` a mým pluginem
- shánění LPS klienta, aby šel projekt rozumně testovat
- vytvoření LSP playgroundu
- `pyls` nepodporuje `DocumentSymbol[]`
	- Issue: https://github.com/palantir/python-language-server/issues/407
	- PR:    https://github.com/palantir/python-language-server/pull/537
	- MS implementace Pythoního ls ho podporuje
- Semantic Tokens je taky zajímavý, ale asi k ničemu: https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens

### 16. 3. 2021
- `Document Color Request` vypadá ~~skvěle~~ nepoužitelně (je jen na barvy): https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentColor
	- poslání stejného range ale v jiných barvách několikrát za sebou by mělo fungovat
	- možná by mohlo jít nějak tweakovat specificky ten plugin, aby se posílaly dané barvy
	- každopádně by bylo fajn mít config, který bude podporovat nějak rozumně zadávat custom theme
- nemůžeme prostě (pro nějaký přenos informací) použít custom registraci a rozšíření language serveru:
	- asi to bude nejlepší, protože nápad s `DocumentSymbols` ten protokol částečně zneužívá
	- https://microsoft.github.io/language-server-protocol/specifications/specification-current/#client_registerCapability
	- nezdá se, že by to `pyls` nějak rozumně podporoval, asi to bude potřeba nějak implementovat
		- https://github.com/palantir/python-language-server/issues/921
- `pyls-fork` se zdá, že bude lepší alternativa do budoucna: https://github.com/python-ls/python-ls
	- zkusit nějaké lehčí věci (přepsat `README` do markdownu) fixnout: https://github.com/python-ls/python-ls/issues/4
- `pytype` existuje: https://github.com/google/pytype
	- funguje výrazně lépe!
	- generuje `.pyi` soubory, které jsou vysloveně anotace proměnných a funkcí
		- ne úplně detailní: https://github.com/google/pytype/issues/861
