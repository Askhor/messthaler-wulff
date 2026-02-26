# General Commands
s/"\(.*\)"/\\textquote{\1}/g
s/N{}/\\mathcal{N}/g
s/>.*COMMENT.*//

# De-Unicode Transformations

## General Unicode Characters
s/:=/\\coloneq/g
s/→/\\rightarrow/g
s/·/\\cdot/g

## Greek Letter definitions
s/δ/\\delta/g
s/Δ/\\Delta/g
s/φ/\\varphi/g
s/χ/\\chi/g
s/ℤ/\\mathbb{Z}/g
s/∘/\\circ/g
s/∩/\\cap/g
s/∪/\\cup/g