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

### 17. 3. 2021
- `pytype` umí `reveal_type(expr)`, což je identické s mypy a asi bude potřeba
	- teoreticky půjde používat oboje? podle toho, která dependence tam je...

### 19. 3. 2021
- `pytype` má v `pytype/tools/traces` věc na řádek-po-řádku vypisování toho, co si o proměnných myslí:

```
1 x = 123
  LOAD_CONST : 123 <- (ClassType(name='builtins.int'),)
  STORE_NAME : x <- (ClassType(name='builtins.int'),)
-------------------
3 def funct() -> int:
  LOAD_NAME : int <- (GenericType(base_type=ClassType(name='builtins.type'), parameters=(ClassType(name='builtins.int'),)),)
  LOAD_CONST : ('return',) <- (TupleType(base_type=ClassType(name='builtins.tuple'), parameters=(ClassType(name='builtins.str'),)),)
  BUILD_CONST_KEY_MAP : __setitem__ <- (ClassType(name='typing.Callable'), ClassType(name='builtins.NoneType'))
  BUILD_CONST_KEY_MAP : __setitem__ <- (ClassType(name='typing.Callable'), ClassType(name='builtins.NoneType'))
  LOAD_CONST : <pytype.blocks.OrderedCode object at 0x7f3c0bc7e4e0> <- (ClassType(name='builtins.code'),)
  LOAD_CONST : funct <- (ClassType(name='builtins.str'),)
  MAKE_FUNCTION : funct <- (CallableType(base_type=ClassType(name='typing.Callable'), parameters=(ClassType(name='builtins.int'),)),)
  STORE_NAME : funct <- (CallableType(base_type=ClassType(name='typing.Callable'), parameters=(ClassType(name='builtins.int'),)),)
-------------------
4     y = 123
  LOAD_CONST : 123 <- (ClassType(name='builtins.int'),)
  STORE_FAST : y <- (ClassType(name='builtins.int'),)
-------------------
6     x = y
  LOAD_FAST : y <- (ClassType(name='builtins.int'),)
  STORE_FAST : x <- (ClassType(name='builtins.int'),)
-------------------
8     return "ahoj"
  LOAD_CONST : ahoj <- (ClassType(name='builtins.str'),)
-------------------
10 for i in range(15):
  LOAD_NAME : range <- (GenericType(base_type=ClassType(name='builtins.type'), parameters=(ClassType(name='builtins.range'),)),)
  LOAD_CONST : 15 <- (ClassType(name='builtins.int'),)
  CALL_FUNCTION : __init__ <- (GenericType(base_type=ClassType(name='typing.Callable'), parameters=(AnythingType(), ClassType(name='builtins.NoneType'))), ClassType(name='builtins.NoneType'))
  CALL_FUNCTION : range <- (GenericType(base_type=ClassType(name='builtins.type'), parameters=(ClassType(name='builtins.range'),)), ClassType(name='builtins.range'))
  GET_ITER : __iter__ <- (CallableType(base_type=ClassType(name='typing.Callable'), parameters=(GenericType(base_type=ClassType(name='typing.Iterator'), parameters=(ClassType(name='builtins.int'),)),)), GenericType(base_type=ClassType(name='typing.Iterator'), parameters=(ClassType(name='builtins.int'),)))
  FOR_ITER : __next__ <- (ClassType(name='typing.Callable'), ClassType(name='builtins.int'))
  STORE_NAME : i <- (ClassType(name='builtins.int'),)
-------------------
11     print(i)
  LOAD_NAME : print <- (GenericType(base_type=ClassType(name='typing.Callable'), parameters=(AnythingType(), ClassType(name='builtins.NoneType'))),)
  LOAD_NAME : i <- (ClassType(name='builtins.int'),)
  CALL_FUNCTION : print <- (GenericType(base_type=ClassType(name='typing.Callable'), parameters=(AnythingType(), ClassType(name='builtins.NoneType'))), ClassType(name='builtins.NoneType'))
  LOAD_CONST : None <- (ClassType(name='builtins.NoneType'),)
-------------------
```
