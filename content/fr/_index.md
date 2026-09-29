---
title: ''
date: '2026-09-10T13:47:59Z'
type: landing
sections:
- block: resume-biography-3
  id: about
  content:
    username: scott
- block: resume-experience
  id: experience
  content:
    username: scott
    title: Expérience Professionnelle
    date_format: Jan 2006
    items:
    - title: Researcher (Chargé de Recherche)
      company: INRAE-PRC
      company_url: https://www6.val-de-loire.inra.fr/physiologie_reproduction_comportements_eng/
      location: Nouzilly, France
      date_start: '2017-11-01'
    - title: Postdoc Research Engineer
      company: Université François-Rabelais de Tours, Inserm, Imagerie et Cerveau UMR U930
      company_url: https://ibrain.univ-tours.fr/english-version-/imaging-brain-702734.kjsp
      location: Tours, France
      date_start: '2015-11-01'
      date_end: '2017-08-31'
    - title: Postdoc Researcher
      company: Laboratoire de Psychologie Cognitive UMR7290, Aix-Marseille Université / CNRS
      company_url: https://lpc.univ-amu.fr/en
      location: Marseille, France
      date_start: '2015-04-01'
      date_end: '2015-10-31'
    - title: Postdoc Researcher
      company: Institut de Neurosciences de la Timone UMR7289, Aix-Marseille Université / CNRS
      company_url: http://www.int.univ-amu.fr/?lang=en
      location: Marseille, France
      date_start: '2013-04-01'
      date_end: '2015-03-31'
    - title: Postdoc Researcher
      company: Indiana University
      company_url: https://psych.indiana.edu
      location: Bloomington, USA
      date_start: '2011-05-01'
      date_end: '2013-03-31'
  design:
    spacing:
      padding:
      - 20px
      - '0'
      - 20px
      - '0'
- block: collection
  id: featured
  content:
    title: Sélection de publications
    filters:
      folders:
      - publication
      featured_only: true
    count: 0
    order: desc
  design:
    view: card
- block: collection
  id: publications
  content:
    title: Publications Récentes
    filters:
      folders:
      - publication
      exclude_featured: false
    count: 5
    order: desc
  design:
    view: citation
- block: collection
  id: projects
  content:
    title: Projets
    filters:
      folders:
      - project
  design:
    view: card
    columns: 2
- block: markdown
  id: tags
  content:
    title: Tags
    text: '[Parcourir tous les tags](/fr/tag/)'
- block: markdown
  id: contact
  content:
    title: Contact
    text: Retrouvez-moi via les liens du profil ci-dessus.
  design:
    columns: '2'
---
