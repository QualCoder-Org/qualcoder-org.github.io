import os

# Dossiers contenant les fichiers Markdown
en_dir = "en"
fr_dir = "fr"

def add_path_metadata(directory, lang):
    """Ajoute le bloc `path` en haut des fichiers Markdown."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, start=directory)
                # Convertir le chemin en format compatible avec MkDocs
                path_value = f"{lang}/{rel_path.replace('.md', '')}"

                with open(filepath, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    # Vérifier si le bloc `path` est déjà présent
                    if not content.startswith("---"):
                        # Ajouter le bloc `path` en haut du fichier
                        new_content = f"---\npath: {path_value}\n---\n\n{content}"
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()
                    else:
                        # Si un bloc YAML existe déjà, ajouter `path` à l'intérieur
                        lines = content.splitlines()
                        if not any(line.strip().startswith("path:") for line in lines):
                            # Trouver la fin du bloc YAML (ligne avec `---` seule)
                            for i, line in enumerate(lines):
                                if line.strip() == "---":
                                    lines.insert(i, f"path: {path_value}")
                                    break
                            new_content = "\n".join(lines)
                            f.seek(0)
                            f.write(new_content)
                            f.truncate()

# Ajouter les métadonnées `path` pour les fichiers en anglais
add_path_metadata(en_dir, "en")

# Ajouter les métadonnées `path` pour les fichiers en français
add_path_metadata(fr_dir, "fr")

print("Les métadonnées `path` ont été ajoutées à tous les fichiers Markdown.")

