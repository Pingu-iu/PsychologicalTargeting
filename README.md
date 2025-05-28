# Experimental evidence of personality alignment effects on ad delivery on Meta

This repository contains the data, analysis code, and survey instruments supporting the study titled **"Experimental Evidence of Personality Alignment Influence on Ad Delivery on Meta"**.

## Overview

This project investigates whether ad delivery algorithms on Meta (Facebook) can facilitate psychological targeting — that is, whether ads aligned with users’ personality traits are preferentially delivered even without explicit targeting instructions. The study uses controlled experiments, including personality-based audience segmentation and randomized ad delivery testing, to audit Meta’s ad delivery system.

## Repository Structure
```
PsychologicalTargeting/
│
├── data/ # Experimental datasets
│ ├── audiences/ # Audience composition and event data (anonymized) 
│ ├── platform_behavior/ # Ad delivery metrics from Meta 
│ ├── surveys/ # Raw and cleaned pilots and final survey responses 
│ └── user_behavior/ # User engagement with ad content (A/B test results) 
│
├── notebooks/ # Jupyter notebooks for data analysis
│ ├── ad_appeal.ipynb
│ ├── audiences.ipynb
│ ├── pilots.ipynb
│ └── main.nb.html # Rendered notebook output
│
├── insights.py # Supporting functions for plotting and campaign result retrieval 
├── utils.py # Helper utilities for campaign details retrieval 
├── main.Rmd # RMarkdown version of main report (if used)
├── .gitignore
└── README.md # This file
```


## Contents

### `/data/audiences/`
Contains audience estimates, tracking data, and events used to build psychometric and behavioral audiences.
Any data that can be used to identify users was removed or anonymized. 

### `/data/platform_behavior/`
Reach and delivery metrics of the ads used in the controlled ad delivery experiments.

### `/data/surveys/`
Survey responses from Prolific (sample from psychometric profiled audiences) and pilots used to validate personality-congruent ad designs.

### `/data/user_behavior/`
Engagement metrics (total likes, comments, shares) from randomized A/B tests conducted on Meta.

### `/notebooks/`
Analysis notebooks for audience construction, ad appeal ratings, and interpretation of delivery outcomes.

## Usage

- To reproduce the analysis, open and execute the notebooks in the `/notebooks/` directory. 
- Survey materials and behavioral results can be accessed in the `/data/` folder.
- `insights.py` contains functions interfacing with the Meta Graph API (Insights API) to programmatically retrieve campaign performance data—reach, impressions, engagement metrics, and cost—across campaigns, ad sets, and individual ads.
- `utils.py` contains functions interfacing Meta Graph API to programmatically retrieve information about campaigns, ad sets, ads, and audiences. 


## License

This work is shared under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/), unless otherwise stated. Please cite appropriately when using or adapting this work.

## Contact

For questions or collaborations, please reach out to the project lead via the corresponding author contact in the associated publication.




