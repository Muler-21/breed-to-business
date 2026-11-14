#!/usr/bin/env bash
# The same analysis as analyse.py, with PLINK 1.9 (for an HPC or a laptop).
# Input: OaSNP2818x28210.{bed,bim,fam} (figshare 26731378, CC BY 4.0, or branch data-sheep).
set -euo pipefail
IN=${1:-OaSNP2818x28210}
POPS="Menz EthiopianMenz Wollo Farta Washera Adile ArsiBale Horro Bonga Doyogena BlHeadedSomali Adane Arabo Kefis Gesses Kido Loya ShubiGemo Hammari Kabashi RedMaasai Dorper LocalAwassi Djallonke Damara EgyptianBarki"
awk -v p="$POPS" 'BEGIN{n=split(p,a," ");for(i=1;i<=n;i++)k[a[i]]=1} ($1 in k){print $1, $2}' "$IN.fam" > keep.txt
P="--sheep --allow-no-sex"
plink $P --bfile "$IN" --keep keep.txt --geno 0.05 --mind 0.10 --maf 0.01 --make-bed --out eth_qc        # QC
plink $P --bfile eth_qc --hardy --out eth_qc                                                              # HWE per SNP
plink $P --bfile eth_qc --het --out eth_qc                                                                # Ho, F per animal
plink $P --bfile eth_qc --indep-pairwise 50 5 0.2 --out prune
plink $P --bfile eth_qc --extract prune.prune.in --pca 10 --out eth_pca                                   # PCA
plink $P --bfile eth_qc --extract prune.prune.in --make-bed --out eth_pruned
for K in 2 3 4 5 6; do admixture --cv eth_pruned.bed $K | tee admixture_K$K.log; done                    # ADMIXTURE (if installed)
plink $P --bfile eth_qc --homozyg --homozyg-kb 4000 --homozyg-snp 25 --homozyg-window-snp 25 \
      --homozyg-window-het 1 --homozyg-het 1 --homozyg-density 250 --homozyg-gap 1000 --out eth_roh      # ROH
awk '{print $1, $2, $1}' eth_qc.fam > clusters.txt
plink $P --bfile eth_qc --within clusters.txt --fst --out eth_fst                                         # FST (Weir & Cockerham)
plink $P --bfile eth_qc --make-grm-bin --out eth_grm 2>/dev/null || echo "use GCTA for GRM: gcta64 --bfile eth_qc --make-grm --out eth_grm"
