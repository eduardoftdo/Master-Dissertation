# UNIRIO PPGI - Master's Dissertation


### Eduardo Furtado
### "A Study on Pre-processing Video Images to Improve the Accuracy of Hand Tremor Classifiers"


Introduction: This repository contains the source code developed for my master's dissertation at UNIRIO PPGI. The aim of the study is to enhance the accuracy of classifiers used in detecting hand tremors, a symptom often associated with Parkinson’s Disease and other neurological conditions.

Background: The study builds upon the work of Yang et al. in "Automatic Detection Pipeline for Assessing the Motor Severity of Parkinson’s Disease in Finger Tapping and Postural Stability" [1]. In their paper, they have collected the PDMotorDB dataset [2] with a rich collection of over 600 participants performing the finger tapping task frequently used by doctor to assess motor severity in hand tremors patients. After providing a signed license agreement, we got access to the dataset for academic purposes, however, although the raw videos are available for others to use in academia, the source code for their methology is not public.

The methodology implemented in this project involves:
- Extracting the tips of the index finger and thumb from source videos using pose estimation techniques.
- Replicating the three features used in Yang et al.'s work.
- Implementing a classifier algorithm based on their methodology.
- Data agumentation by rotating and mirroring the videos.

Additional Contributions:
Originally, this project intended to collaborate with a doctor from the HUGG College Hospital to record and share a new dataset, with a simple to use web solution, a Video Collection Platform. However, due to the extended approval process required by the university's ethics committee, we were unable to complete this within our timeframe. Despite this, the platform and methodology developed here are shared with the community. This platform is designed for medical professionals to track patients' disease progression recording their sessions, while it generates a dataset that can be used for training AI-assisted tools, aiding doctors in early diagnosis. Furthermore, the code and methodology provided can be used by other researchers to collect similar datasets. It is also adaptable for various tasks beyond recording hand videos, offering a versatile tool for different research and medical applications.



References:
[1] https://doi.org/10.1109/ACCESS.2022.3183232
[2] https://github.com/pddata/PDMotorDB
