
import os

# Obtendo o diretório base do projeto (subindo um nível)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construindo os caminhos relativos a partir do diretório base ajustado
file_path = os.path.join(base_dir, 'mt3', 'mt3', 'gin', 'model.gin')

print(base_dir)
print(file_path)