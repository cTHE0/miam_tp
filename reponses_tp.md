# TP Identification - Réponses

## 1. Utilisation du code de calcul par éléments finis

### Extraction des mesures

On utilise `readMeasurement` pour charger les données. Pour le cas inhomogène (fichiers `measure_sb.npz` et `measure_sb_Pi.npz`), on obtient :

- phi1 = 0.1955, phi2 = -0.0666, phi3 = -0.0624, phi4 = -0.0666
- um : champ de pression sur 803 noeuds, compris entre 0 et 1
- Pi : projecteur 4x803 tel que Pi @ um = [P1, P2, P3, P4]
- Pm = Pi @ um, le vecteur de mesures

Pour le cas homogène (`measure_sb_H.npz`), les flux sont proches mais différents :
- phi1 = 0.1890, phi2 = -0.0654, phi3 = -0.0583, phi4 = -0.0653

### Fonction de calcul direct

J'ai créé une fonction `calcul_direct(mesh, k1, k2, phi)` qui :

1. Assemble les matrices EF élémentaires (via `ElMats`)
2. Construit K0 avec `assemK` en utilisant `paramdict = {1: k1, 2: k2}`
3. Impose les conditions de Neumann : sur chaque buse, le flux normal est `phi_i / L` où L = 0.02 mm est la largeur d'une buse. Le dictionnaire Neumann est `{1: phi1/L, 2: phi2/L, 3: phi3/L, 4: phi4/L}`
4. Impose la pression nulle au noeud 0 via `DirichletScalar` avec `zerozero=True` pour fixer la constante
5. Résout K p = f avec `spsolve`
6. Applique la translation (équation 4) pour recaler la solution sur les mesures

La translation consiste à calculer :
```
t = 1/4 * sum( (Pi @ um)_i - (Pi @ p)_i )
p_corrige = p + t
```

### Comparaison avec um

La solution obtenue n'est pas parfaitement égale à `um`, même avec les bons paramètres k1=1, k2=2. La différence vient du fait que :

- Le problème direct utilise des conditions de Neumann (flux imposés) alors que la mesure `um` a été générée avec des conditions de Dirichlet (pressions imposées)
- Même avec la translation, les champs ne sont pas identiques car la translation ne corrige qu'un décalage constant, pas les éventuelles différences de forme du champ
- Les flux phi1..phi4 imposés en Neumann sont des valeurs scalaires (intégrales) et on perd donc de l'information par rapport au champ complet

Conséquence sur l'identification : le résidu ne pourra jamais être nul, même avec les vrais paramètres. L'identification se fait au mieux, avec un résidu minimum non nul.

## 2. Identification par substitution (méthode des sensibilités)

### 2.1 Cas à un paramètre

J'utilise les mesures homogènes (`measure_sb_H`). La valeur cible est k_ref = 1.

J'implémente l'algorithme de Newton :

1. Initialiser k = k0 (par exemple k0 = 0.5)
2. Pour chaque itération :
   - Calculer p0 avec `calcul_direct` pour le paramètre k
   - Pour d = 1 (une seule dimension), perturber k de epsilon : k_tilde = k + epsilon
   - Calculer pd avec k_tilde
   - J = (pd - p0) / epsilon (différences finies)
   - S = Pi @ J (matrice de sensibilité)
   - g = S.T @ (Pi @ p0 - Pm)
   - H = S.T @ S
   - delta = résoudre H delta = g
   - k = k - delta

J'ai tracé les courbes :
- Le résidu (norme de Pi @ p - Pm) décroît rapidement puis se stabilise
- L'erreur |k - k_ref| converge vers une valeur proche de 0

La convergence est bonne car le problème à 1 paramètre est bien conditionné. On retrouve bien k ≈ 1.

### 2.2 Cas à deux paramètres

J'utilise les mesures inhomogènes (`measure_sb`). Les valeurs cibles sont k1_ref = 1, k2_ref = 2.

L'algorithme est le même mais avec 2 dimensions :
- J a 2 colonnes : une pour la perturbation de k1, une pour k2
- H est une matrice 2x2
- g est un vecteur de taille 2

J'ai testé plusieurs points de départ :

| k0 initial | k trouvé | Résidu final |
|-----------|----------|--------------|
| (0.5, 1)  | proche de (1, 2) | faible |
| (2, 1)    | proche de (1, 2) | faible |
| (5, 5)    | s'éloigne ou converge mal | élevé |

Observations :
- Le résidu décroît en quelques itérations
- L'erreur en norme 2 diminue mais peut stagner si le point de départ est trop éloigné
- Le problème est mal conditionné quand k1 et k2 sont très différents
- La sensibilité au paramètre du disque central (k2) est plus faible, ce qui rend son identification plus difficile

La précision est bonne quand on part de valeurs raisonnables, mais se dégrade pour des points initiaux trop éloignés à cause du mauvais conditionnement de la Hessienne.

## Conclusion

Ce TP a montré la mise en oeuvre d'une méthode d'identification de paramètres par éléments finis.

**Importance de la précision du modèle :** Le modèle EF utilisé (maillage, conditions aux limites) influence directement la qualité de l'identification. Une différence entre le modèle direct et le modèle ayant généré les mesures (Neumann vs Dirichlet) introduit une erreur irréductible. Si le modèle est trop grossier, l'identification sera imprécise.

**Fonctionnement de la régularisation :** La régularisation de Tikhonov ajoute un terme `mu/2 * ||k - kv||^2` à la fonction coût. Cela pénalise les grandes déviations par rapport à une valeur a priori kv. Mathématiquement, cela revient à ajouter `mu*I` à la Hessienne, ce qui améliore son conditionnement. Un grand `mu` force la solution vers `kv`, au détriment de l'ajustement aux données. C'est un compromis biais/variance classique.

**Temps de calcul et performances :** La méthode de Newton (substitution) converge en peu d'itérations (3-5) mais chaque itération coûte cher car elle demande D+1 résolutions EF (D = nombre de paramètres). La méthode adjointe ne demande que 2 résolutions par itération, mais converge beaucoup plus lentement à cause du mauvais conditionnement. Un linesearch ou une méthode de quasi-Newton (BFGS) améliorent la convergence de la méthode adjointe. Dans tous les cas, le pré-calcul des matrices élémentaires (une fois pour toutes) est crucial pour les performances.
