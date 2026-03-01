import torch
import transformers
import ripser
import gudhi
import freud
import sklearn
import numpy as np
import pandas as pd

print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("Transformers:", transformers.__version__)
print("Ripser:", ripser.__version__)
print("Gudhi:", gudhi.__version__)
print("Freud:", freud.__version__)
print("PyTorch:", torch.__version__)
print("All imports successful!")