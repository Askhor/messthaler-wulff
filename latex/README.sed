# General Commands
s/"\(.*\)"/\\textquote{\1}/
s/N{}/\\mathcal{N}/
s/>.*COMMENT.*//

# De-Unicode Transformations

## General Unicode Characters
s/:=/\\coloneq/
s/→/\\rightarrow/
s/·/\\cdot/

## Greek Letter definitions
s/δ/\\delta/