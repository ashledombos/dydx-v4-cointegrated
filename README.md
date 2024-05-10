Ce bot de trading automatique utilise l'API v4 de dYdX pour exécuter des ordres de trading sur le marché des cryptomonnaies. Il est conçu pour fonctionner avec les clients Python de dYdX et gérer dynamiquement les positions basées sur des paramètres configurables.

## Prérequis

- Python 3.8 ou plus récent.
- pip pour la gestion des paquets Python.
- Un environnement virtuel Python (recommandé).

## Configuration

Avant de lancer le bot, assurez-vous que toutes les dépendances nécessaires sont installées et que l'environnement est correctement configuré.

### Installation des Dépendances

Créez et activez un environnement virtuel, puis installez les dépendances requises :

```bash
python -m venv venv
source .venv/bin/activate  # Sur Windows utilisez `venv\Scripts\activate`
pip install -r requirements.txt
