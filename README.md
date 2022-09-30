# AlgorithmicEditor_Plugins

## Plugins
See [in the main repository](https://github.com/megat69/AlgorithmicEditor_Plugins) for the app.

***ENGLISH***
Plugins are a great tool offered to you by the editor, and allow to extend its functionality with official or third-party applets.<br>
They can add custom commands, custom behaviour, custom syntax highlighting, and much, much more.<br>
As of today, official plugins include, but are not restricted to :
- `autocomplete`, a plugin granting you access to autocompletion in the editor ;
- `ctrl_del`, a plugin giving you access to a command able to erase the current word in one keystroke, like the Ctrl + Del keybind ;
- `docstring`, which automatically setups information for functions in a single keybind ;
- `paste`, which lets you paste anything from your clipboard to the editor ;
- **And most importantly,** `plugin_repo`, which is the heart of the plugins : it allows you to manage (enable/disable/delete/list) your plugins or download/updates new ones.
  - It is the only plugin downloaded by default (if you select so in the setup).

***FRANÇAIS***
Les plugins sont d'excellents outils proposés par l'éditeur, et vous permettent d'étendre ses fonctionnalités avec des applets officiels ou tiers.<br>
Ces derniers peuvent ajouter des commandes personnalisées, de la logique personnalisée, une coloration syntaxique personnalisée, et bien plus encore.<br>
Au moment de l'écriture de ces lignes, les plugins officiels contiennent, mais ne sont pas restreints à :
- `autocomplete`, un plugin vous donnant accès à une autocomplétion dans l'éditeur ;
- `ctrl_del`, un plugin vous donnant accès à une commande capable d'effacer le mot sélectionné en une touche, comme le raccourci Ctrl + RetourArrière ;
- `docstring`, qui vous met en place automatiquement les informations demandées pour la création de fonctions (Données, préconditions, etc.) en une seule touche ;
- `paste`, qui vous permet de coller n'importe quoi de votre presse-papiers dans l'éditeur ;
- **Et le plus important,** `plugin_repo`, qui est au cœur de tous les plugins : il vous permet de gérer (activer/désactiver/supprimmer/lister) vos plugins, ou d'en télécharger/mettre à jour d'autres.
  - Il s'agit du seul plugin téléchargé par défaut (si vous acceptez durant le setup).

## How to create a plugin ?
***ENGLISH***<br>
Creating a plugin requires very little knowledge of Python. If you know about classes and inheritance, then you should be good to go.<br>
Before creating a plugin, you should look into the `Plugin` class (`plugin.py`) and the source code of official plugins to see how they work behind the hood ; `paste` and `autocomplete` are pretty good examples. *Some are poorly made though, so be aware.*

***FRANÇAIS***<br>
Créer un plugin demande assez peu de connaissances de Python. Si vous connaissez les notions de classes et d'héritage, vous devriez pouvoir vous en sortir.<br>
Avant de créer un plugin, vous devriez jeter un coup d'oeil à la classe `Plugin` (`plugin.py`) et le code source de quelques plugins officiels pour voir leur manière de fonctionner ; `paste` et `autocomplete` sont de bons exemples. *Attention, certains plugins sont fais à la va-vite et mal codés, ne prenez pas exemple sur eux.*


