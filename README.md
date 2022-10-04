# AlgorithmicEditor_Plugins

![image](https://img.shields.io/github/languages/code-size/megat69/AlgorithmicEditor_Plugins)
![image](https://img.shields.io/tokei/lines/github/megat69/AlgorithmicEditor_Plugins)
![image](https://img.shields.io/github/commit-activity/m/megat69/AlgorithmicEditor_Plugins)

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
First of all, you should download the `plugin_repo`. It will allow you to reload your plugin within the editor instead of having to reboot it every time you change something.<br>
Then, you should create a Python file within the `plugins` folder of the editor, with whichever name you want, as long as it has the `.py` extension.<br>

This file will contain all your plugin's code, as plugins are *(at least at the moment)* single-file only.

If you need to work with multiple files, you may create/download them yourself from the plugin file.<br>
*Tip : The `requests` module is great for this purpose, and is already a dependency of the editor.*

If you need to install dependencies, you may install them yourself.<br>
*Tip : The `os.system()` function can serve this purpose.*

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

***FRANÇAIS***<br>
Tout d'abord, vous devriez télécharger le `plugin_repo`. Il vous permettra de recharger votre plugin depuis l'éditeur au lieu d'avoir à le redémarrer à chaque modification.<br>
Ensuite, il vous faudra créer un fichier Python dans le dossier `plugins` de l'éditeur, avec le nom que vous voulez, tant qu'il a l'extension `.py`.<br>

Ce fichier va contenir le code de votre Plugin, vu que les plugins sont *(au moins pour le moment)* single-file (fichier unique) uniquement.

Si vous devez travailler avec plusieurs fichiers, vous devrez les créer/télécharger vous-même depuis le fichier du plugin.<br>
*Conseil : Le module `requests` est parfait pour cette utilisation, et est déjà une dépendance de l'éditeur.*

Si vous devez installer des dépendances, il vous faudra les faire installer vous-même.<br>
*Conseil : La fonction `os.system()` peut servir à ça.*

Une fois que ce fichier est créé, copiez ce code par défaut dedans :
```python
from plugin import Plugin

class NomDeVotrePlugin(Plugin):
    def __init__(self, app):
        super().__init__(app)


def init(app):
    return NomDeVotrePlugin(app)
```
*(Évidemment, remplacez `NomDeVotrePlugin` par le nom de votre plugin.)*

### The Plugin class
***ENGLISH***<br>
As you can see, you get access to an attribute named `app`. Well, it is none other than the main application class itself. So, if you use `self.app`, you can access any of the app's attributes and methods. I recommend you to check them out, they're all documented in the code.

You will also get access to two other attributes : `plugin_name` and `config`, and this as soon as `Plugin.init()` is called (see below).<br>
The first attribute grants you access to the name of your plugin (litterally the name of the file), and the second is a dictionary containing all the config options you already created or set.<br>
Those options are saved upon editor closing.<br>
For a good example of their use, look at how the `autocomplete` plugin works.

The `Plugin` class will grant you access to a few functions that you might find useful when creating a plugin. It's up to you to use them or not, please also note that you can also create your own methods for your class.<br>
Those functions include :
- `init()` : Allows you to log a message, or basically do any task once the plugin is loaded.
  - Beware, just like `__init__(app)`, it is ran BEFORE curses wraps around `main`. Accessing curses methods at this point will simply crash the editor. *This behaviour might get changed in the future.*
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
- `update_on_compilation(final_compiled_code:str, compilation_type:str)` : This method will be called upon compilation of the pseudocode in either algorithmic code or C++.
  - It takes as argument the final compiled code, which is one very long string.
  - The second argument is the compilation type, so whether it was compiled in C++ or Algorithmic. It will thus either take the value "cpp" or "algo".

***FRANÇAIS***<br>
Comme vous pouvez le voir, vous recevez l'accès à un attribut nommé `app`. Eh bien, il s'agit de l'application principale. Ainsi, si vous utilisez `self.app`, vous pouvez accéder à n'importe lequel des attributs ou méthodes de l'éditeur. Je vous recommande d'aller regarder la classe `App` et ses attributs, ils sont tous documentés dans le code *(en anglais uniquement)*.

Vous aurez aussi accès à deux autre attributs : `plugin_name` et `config`, et ce dès l'appel de `Plugin.init()` (voir plus bas).<br>
Le premier donne accès au nom de votre plugin (littéralement le nom du fichier), et le second est un dictionnaire contenant les options de config que vous avez déjà créées ou modifiées.<br>
Ces options sont enregistrées lors de la fermeture de l'éditeur.<br>
Pour un bon exemple de leur utilisation, regardez comment le plugin `autocomplete` fonctionne.

La classe `Plugin` vous donnera accès à quelques fonctions qui pourront vous être utiles lors de la création d'un Plugin. Vous pouvez les utiliser ou non, veuillez noter que vous pouvez aussi créer vos propres méthodes pour votre classe.<br>
Ces fonctions sont :
- `init()` : Vous permet de logger un message, ou faire ce que vous voulez dès que le plugin est chargé.
  - Attention, de la même manière que `__init__(app)`, la fonction est lancée AVANT que curses n'injecte ses variables dans `main`. Accéder à des méthodes/variables curses dans cette fonction va simplement crasher l'éditer. *Ce fonctionnement pourra être changé dans le futur.*
- `add_command(character:str, function:Callable, description:str, hidden:bool = False)` : Probablement la méthode la plus intéressante, la méthode `add_command` va simplement... Eh bien, créer une commande.
  - La plupart des plugins officiels l'utilisent, si vous souhaitez regarder comment ils fonctionnent.
  - Elle prend comme paramètres : 
    - Le caractère qui suivra le symbole de commande pour déclencher la commande (e.g. si votre commande est déclenchée par `:a`, alors ce caractère `'a'`) ; 
    - Ensuite se trouve la fonction qui sera appelée quand la commande sera déclenchée (il peut s'agir d'une lambda, une partial, une méthode de classe, ou une fonction classique, n'importe quel Callable/fonction callback) ;
    - Suivi par un *TRÈS* court titre pour la fonction (vu le peu d'espace à l'écran, ne la faites pas plus longue que 20 caractères, même si c'est possible et permis) ;
    - Et pour finir un booléen indicant si la fonction devrait être cachée ou non (si vous trouvez que cette fonction n'est pas si importante, veuillez mettre cette option à True, et votre commande ne sera affichée que dans la liste des commandes).
- `update_on_keypress(key:str)` : Cette méthode est exécutée chaque fois que l'utilisateur presse une touche. La touche pressée par l'utilisateur vous sera aussi donnée.
  - Notez que si vous décidez de ne pas utiliser la touche, cette méthode peut devenir une méthode update executée à chaque frame.
- `update_on_syntax_highlight(line:str, splitted_line:list, i:int)` : Cette méthode sera appellée n fois à chaque frame, où n correspond en au nombre de lignes dans la variable `app.current_text`.
  - Cette méthode va vous permettre d'ajouter une coloration syntaxique personnalisée sur n'importe quelle ligne.
  - `line` représente la ligne courante, `splitted_line`, une version de cette même ligne séparée sur les espaces, et `i` sa coordonnée y.
- `update_on_compilation(final_compiled_code:str, compilation_type:str)` : Cette méthode sera appelée à la fin de la compilation de pseudocode vers algorithmique ou C++.
  - Le premier argument est le code compilé final, qui est une très longue chaîne de caractères.
  - Le deuxième argument est le type de compilation, donc si il s'agit d'une compilation vers C++ ou Algorithmique. Il prendra donc la valeur "cpp" ou "algo".


## Uploading your plugin
***ENGLISH***<br>
Simply fork and clone this repo, then add your plugin, and create a pull request. I will then have to manually merge it to the repo. At this point, it will be accessible for anyone to download from the `plugin_repo`.

***FRANÇAIS***<br>
Créez un fork de ce dépôt, puis clonez-le, ajoutez votre plugin, et créez une pull request. J'aurai ensuite à le fusionner manuellement vers le dépôt. À partir de là, il sera accessible pour n'importe qui de le télécharger depuis le `plugin_repo`.
