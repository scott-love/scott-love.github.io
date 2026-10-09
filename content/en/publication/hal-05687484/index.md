---
title: '3DBrainMiner: An open-source platform for modelling and visualizing the brain as graphs'
authors:
- Antoine Bourlier
- Scott Love
- Mohamed Slimane
- Titouan Hinschberger
- Jean-Yves Ramel
- Elodie Chaillou
date: '2026-10-01T00:00:00Z'
publication_types:
- article-journal
publication: Neurocomputing
abstract: Graph-based modeling is widely used to represent the structural and functional complexity of the brain, supporting applications such as disease prediction, pathology characterization, and the identification of functional connectivity hubs. Graph theory provides analytical tools for extracting meaningful patterns from neuroimaging data, and graph-based learning approaches, including Graph Neural Networks, have demonstrated improved performance over traditional classifiers. A critical step in this process is graph construction from MRI data. Conventionally, nodes correspond to anatomically defined brain regions derived from atlases, while edges represent structural or functional connectivity inferred from tractography or functional MRI. However, atlas-based segmentation requires expert anatomical knowledge and may be unavailable, incomplete, or inconsistent across species. Similarly, connectivity-based edge definition often relies on partial or uncertain prior knowledge. To address
  these limitations, we propose an alternative framework in which nodes and edges are constructed without relying on prior anatomical knowledge. In this approach, nodes are derived directly from intrinsic image properties, such as voxel intensity and spatial organization, while edges are defined using quantitative attributes including intensity differences, surface contact area, or spatial distance. This strategy enables the generation of multiple graph representations from a single MR image. We introduce 3DBrainMiner, a platform designed to facilitate graph creation, management, and visualization with or without anatomical priors. Its flexibility is demonstrated through applications to a quail brain template and a human brain dataset.
hugoblox:
  ids:
    hal: hal-05687484
    doi: 10.1016/j.neucom.2026.134240
links:
- type: url
  url: https://hal.inrae.fr/hal-05687484v1
---
