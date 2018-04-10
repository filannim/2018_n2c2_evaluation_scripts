# 2018 N2C2 Shared Tasks Evaluation Scripts

This script is distributed as part of the 2018 N2C2 tasks.

If you would like to contribute to this project, pull requests are welcome.
Please see: [here](https://help.github.com/articles/fork-a-repo) for instructions
on how to make a fork of this repository, and
[here](https://help.github.com/articles/using-pull-requests) for instructions
on making a pull request. Suggestions for improvements, bugs or feature
requests may be directed to the 2016 CEGS N-GRID evaluation scripts' [issues
page](https://github.com/filannim/2018_N2C2_evaluation_scripts/issues)






## Setup

This is a Python 3 script and it doesn't require Python external packages.






## Running the script

This script is intended to be used via command line:
```shell
$ python track1_eval.py GOLD SYSTEM
```

It produces performance scores for Track 1 (de-identification).
SYSTEM and GOLD must be directories.

## Output for Track 1: Cohort Selection for Clinical Trials

To compare your system output, run the following command on directories:
```shell
$ python track1_eval.py {gold}/ {system}/
```
(replace the folder names in {}s with the names of your actual folders)

Running it will produce output that looks like this:

```
******************************************* TRACK 1 ********************************************
                      ------------ met -------------    ------ not met -------    -- overall ---
                      Prec.   Rec.    Speci.  F(b=1)    Prec.   Rec.    F(b=1)    F(b=1)  AUC
           Abdominal  0.6167  0.6916  0.7459  0.6520    0.8036  0.7459  0.7736    0.7128  0.7187
        Advanced-cad  0.8235  0.7412  0.7712  0.7802    0.6741  0.7712  0.7194    0.7498  0.7562
       Alcohol-abuse  0.0946  0.7000  0.7590  0.1667    0.9860  0.7590  0.8577    0.5122  0.7295
          Asp-for-mi  0.9235  0.7870  0.7414  0.8498    0.4674  0.7414  0.5733    0.7115  0.7642
          Creatinine  0.6159  0.8019  0.7088  0.6967    0.8600  0.7088  0.7771    0.7369  0.7553
       Dietsupp-2mos  0.7417  0.7517  0.7194  0.7467    0.7299  0.7194  0.7246    0.7357  0.7356
          Drug-abuse  0.1264  0.7333  0.7216  0.2157    0.9801  0.7216  0.8312    0.5235  0.7275
             English  0.9750  0.7358  0.7826  0.8387    0.2045  0.7826  0.3243    0.5815  0.7592
               Hba1c  0.6818  0.7353  0.8118  0.7075    0.8483  0.8118  0.8297    0.7686  0.7736
            Keto-1yr  0.0149  1.0000  0.7700  0.0294    1.0000  0.7700  0.8701    0.4497  0.8850
      Major-diabetes  0.7222  0.7500  0.6591  0.7358    0.6905  0.6591  0.6744    0.7051  0.7045
     Makes-decisions  0.9906  0.7617  0.8182  0.8612    0.1200  0.8182  0.2093    0.5353  0.7900
             Mi-6mos  0.2840  0.8846  0.7786  0.4299    0.9855  0.7786  0.8699    0.6499  0.8316
                      ------------------------------    ----------------------    --------------
     Overall (micro)  0.6952  0.7546  0.7493  0.7237    0.8012  0.7493  0.7744    0.7490  0.7520
     Overall (macro)  0.5855  0.7749  0.7529  0.5931    0.7192  0.7529  0.6950    0.6440  0.7639

                                                   288 files found
```

A few notes to explain this output:
- The "288" represents the number of files the script was run on. This means that 288 files have the same names in both the input folders.
- The official ranking measure is Overall (micro) F(b=1) (0.7490 in the example above).

### Categories

- Abdominal
- Advanced-cad
- Alcohol-abuse
- Asp-for-mi
- Creatinine
- Dietsupp-2mos
- Drug-abuse
- English
- Hba1c
- Keto-1yr
- Major-diabetes
- Makes-decisions
- Mi-6mos