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
### Basics
***ENGLISH***<br>
Creating a plugin requires very little knowledge of Python. If you know about classes and inheritance, then you should be good to go.<br>
Before creating a plugin, you should look into the `Plugin` class (`plugin.py`) and the source code of official plugins to see how they work behind the hood ; `paste` and `autocomplete` are pretty good examples. *Some are poorly made though, so be aware.*

***FRANÇAIS***<br>
Créer un plugin demande assez peu de connaissances de Python. Si vous connaissez les notions de classes et d'héritage, vous devriez pouvoir vous en sortir.<br>
Avant de créer un plugin, vous devriez jeter un coup d'oeil à la classe `Plugin` (`plugin.py`) et le code source de quelques plugins officiels pour voir leur manière de fonctionner ; `paste` et `autocomplete` sont de bons exemples. *Attention, certains plugins sont fais à la va-vite et mal codés, ne prenez pas exemple sur eux.*

### Getting started
***ENGLISH***<br>
First of all, you should download the `plugin_repo`. It will allow you to reload your plugin within the editor instead of having to reboot it every time.<br>
Then, you should create a Python file within the `plugins` folder of the editor, with whichever name you want, as long as it has the `.py` extension.<br>

This file will contain all your plugin's code, as plugins are *(at least at the moment)* single-file only.

Once the file is created, copy this boilerplate into it :
```python
from plugin import Plugin

class YourPluginName(Plugin):
    def __init__(self, app):
        super().__init__(app)


def init(app):
    return YourPluginName(app)
```
*(Obviously replace `YourPluginName` with the name of your plugin.)*

### The Plugin class
***ENGLISH***<br>
As you can see, you get access to an attribute named `app`. Well, it is none other than the main application class itself. So, if you use `self.app`, you can access any of the app's attributes and methods. I recommend you to check them out, they're all documented in the code.

The `Plugin` class will grant you access to a few functions that you might find useful when creating a plugin. It's up to you to use them or not, please also note that you can also create your own methods for your class.<br>
Those functions include :
- `init()` : Allows you to log a message, or basically do any task once the plugin is loaded.
  - Beware, just like `__init__(app)`, it is ran BEFORE curses wraps around main. Accessing curses methods at this point will simply crash the editor. *This behaviour might get changed in the future.*
- `add_command(character:str, function:Callable, description:str, hidden:bool = False)` : Probably the most interesting method, the `add_command` method will simply... Well, create a command.
  - Most official plugins do that, if you want to check on how they do.
  - It takes as arguments : 
    - the character that will follow the command symbol to trigger the function (e.g. if your command is triggered by `:a`, then this character is `'a'`) ; 
    - Following is the function that is going to be called upon function trigger (it can be a lambda, a partial, a class method, a regular function, any Callable/callback function really) ;
    - Then a *VERY* short title for the function (the screen space being so cramped as is, don't make it any longer than 20 characters, although it is technically possible and allowed) ;
    - And finally a boolean indicating whether the function should be hidden (if you deem the function not so important, please put this option to True, and your command will be only shown in the commands list).
- `update_on_keypress(key:str)` : This method is ran every time the user presses a key. The key pressed by the user will also be given.
  - Note that if you simply don't use the key, this method can become an update method ran every frame.
- `update_on_syntax_highlight(line:str, splitted_line:list, i:int)` : This method will be called n times each frame, where n is the amount of lines in the `app.current_text` variable.
  - This method will allow you to add custom syntax highlighting to any line.
  - `line` represents the current line, `splitted_line`, a version split on spaces, and `i` its y coordinate.
  - A great example of how to use this method is in the `docstring` plugin.
- `update_on_compilation(final_compiled_code:str, compilation_type:str)` : This method will be called upon compilation of the pseudocode in either algorithmic code or C++.
  - It takes as argument the final compiled code, which is one very long string.
  - The second argument is the compilation type, so whether it was compiled in C++ or Algorithmic. It will thus either take the value "cpp" or "algo".
