import numpy as np
import torch
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModel
from ripser import ripser
from persim import plot_diagrams, PersistenceImager
import nltk

# Ensure you have sentence splitting capability
nltk.download('punkt')
from nltk.tokenize import sent_tokenize


def get_sentence_embeddings(text, model_name="allenai/specter2_base"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Split abstract into sentences
    sentences = sent_tokenize(text)
    print(sentences)

    embeddings = []
    for sentence in sentences:
        # SPECTER2 expects title + abstract; for sentences we use the sentence as both
        inputs = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt", max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        # Use CLS token as sentence representation
        embeddings.append(outputs.last_hidden_state[:, 0, :].numpy())

    return np.vstack(embeddings)


# Your two abstracts
abstract_1 = "The rapid integration of generative artificial intelligence (genAI) into knowledge-intensive work represents a fundamental shift in how human ideas are articulated and transmitted. As academic and professional writing move from human-centric to AI-co-produced workflows, the structural integrity of our collective knowledge systems faces an unprecedented challenge. While genAI enhances individual productivity, it operates on probabilistic models that favour statistical averages, potentially compressing the semantic space available for novel discovery. This project develops a pioneering diagnostic framework to evaluate the long-term impact of AI-mediated writing on the diversity and resilience of knowledge systems. The research leverages Topological Data Analysis (TDA), specifically persistent homology—a method that tracks how connectivity, loops, and higher-order structural patterns emerge and persist as data resolution changes (Carlsson, 2009). This allows the project to move beyond surface-level text evaluation to identify deep structural shifts, such as “homogenisation loops” or the loss of conceptual frontiers, that standard statistical methods cannot detect. Drawing on a career trajectory that bridges computational physics and cybernetics, I am uniquely positioned to lead this project. My research focuses on the development of interdisciplinary frameworks that leverage computational tools to identify emerging structural motifs and quantify the information flow within complex systems. By applying these methods to the knowledge ecosystem, I will deliver a robust toolkit for assessing whether our digital knowledge landscapes—the high-dimensional semantic spaces representing how research is formulated—remain structurally open and exploratory or are converging toward stagnant, self-referential configurations. These insights are critical for safeguarding the long-term resilience of Australia’s research integrity and innovation capacity in an era of pervasive AI assistance. Innovation rarely happens through incremental improvements on the “average” idea; rather, it emerges from the productive tension between divergent thinking—the ability to explore wild, distant, and non-obvious ideas—and convergent thinking—the ability to synthesise those ideas into meaningful outputs. GenAI, by its very design, is a “super-convergent” engine. It functions by predicting the most statistically probable next word or concept based on existing data. Over-reliance on genAI to co-produce knowledge inadvertently introduces a feedback loop that traps outputs within the semantic mean, creating a “compression of novelty”. There is a significant gap in research addressing the long-term structural evolution of the broader knowledge ecosystem. Recent evidence confirms that while AI can boost individual creativity, it simultaneously narrows narrative diversity at a collective scale (Doshi & Hauser, 2024). Crucially, this deskilling is a structural problem rather than an issue of individual agency; as Ferdman (2025) argues, AI’s influence creates systemic conditions that undermine the very process of capacity cultivation, inhibiting the development and exercise of human cognitive abilities. However, there is currently no established methodology to quantify this systemic thinning of ideas."
abstract_2 = "The collective organization of interacting agents often gives rise to polarized domains across a wide range of biological and non-biological systems. It is generally recognized that the absence of a characteristic domain size—i.e., scale-free behavior—signals a system’s capacity for robust collective response to sudden perturbations. In this study, we employ a computational framework based on Lloyd’s algorithm to evolve a two-dimensional disordered point pattern into a hyperuniform configuration using a simple interaction rule governed by local geometric and topological relationships between each point and its nearest neighbors. Throughout the ordering transition, hexagonal domains with aligned orientations emerge and are separated by non-hexagonal topological defects. As the system size increases, corresponding to a larger number of interacting points, we observe that the size of orientationally correlated domains in the converged hyperuniform state scales linearly with system size, indicating scale-free correlations. Unlike prior studies that primarily emphasize dynamic variables such as velocity fields, our work highlights the static geometric properties of ordered domains. This geometric perspective offers new insights into collective organization and emergent behavior in complex systems."

# 1. Generate Embeddings (Point Clouds)
model = "allenai/specter2_base"    #'sentence-transformers/all-mpnet-base-v2'
pc1 = get_sentence_embeddings(abstract_1, model)
pc2 = get_sentence_embeddings(abstract_2, model)

# 2. Compute Persistent Homology
# We look for H0 (connectivity) and H1 (loops/cycles in the logic)
dgms1 = ripser(pc1)['dgms']
print(dgms1)
dgms2 = ripser(pc2)['dgms']
print(dgms2)

# 3. Visualization
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

plot_diagrams(dgms1, show=False, ax=axs[0])
axs[0].set_title("Abstract 1: Original Persistence Diagram")

plot_diagrams(dgms2, show=False, ax=axs[1])
axs[1].set_title("Abstract 2: Rephrased Persistence Diagram")

plt.tight_layout()
plt.savefig("persistence_comparison.png")

# 4. Persistence Landscapes (using a simple vectorization for comparison)
# Landscapes help quantify the "height" of the topological features
pimgr = PersistenceImager(pixel_size=0.1)
imgs1 = pimgr.transform(dgms1[1])  # Focus on H1 (structural loops)
imgs2 = pimgr.transform(dgms2[1])

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(imgs1, cmap="Accent")
plt.title("Landscape H1: Abstract 1")
plt.subplot(1, 2, 2)
plt.imshow(imgs2, cmap="Accent")
plt.title("Landscape H1: Abstract 2")
plt.savefig("landscape_comparison.png")