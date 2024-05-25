# Ravlt Audio Gui

In this folder, you'll find a
1) environment.txt or environment.yml (should be interchangeable for our purposes) which lists all the dependencies needed for this project. You can make a new conda environment using:
```bash
conda env create -f environment.yaml
```
or simply create an empty environment and import the dependencies listed in req.txt manually
```bash
conda create --name my_environment
```

2) the main file called ravlt_audio_gui.py. You can run this file by typing the following command into the terminal
```bash
python ravlt_audio_gui.py
```

**USAGE**

3) After launching the code, a dialog box prompting the user to input their initials. This is just to keep of what member's making what edits.
4) After pressing 'Submit', a GUI will appear.
5) **Getting Started**: Press *Import* to import a partcipant folder listing the audio transcriptions. Once imported, you'll see 2 other windows populate: the *Top Left* displays the .csv as edits are made; the *Top Right* displays the waveform for the audio (this will be necessary for making *Edits* and *Inserts* (see below).
6) Once imported, the name of the block (e.g. Block 1 Recall) will apppear in the *Left Column*. Once ready to begin, press *Start* and the audio will begin playing. Upon pressing *Start*, the current word will appear at the bottom of the *Middle Column* as well as be highlighted in the *Top Left* window.
7)  **Quality Check**: *Bottom Right of GUI* Once the audio plays, the *first* thing we want to check if the speech was correctly transcribed. You do this by pressing *Accept* to validate the transcription, *For Review* for audio that may be inaudible and needs an additional listening, and *Off Task* for any speech that was not an attempt to recall a word from the list (e.g. 'I'm tired', 'My parent shoud be coming to pick me up soon'). Additionally, you can press *Add Note* to add any information about a decision related to the quality check or edits.
8)  *Important Note*: For an utterance to qualify as *Off Task*, it must not relate at all to the task. Any repeats, mistakes (e.g. says 'drape' rather than 'curtain'), subvocalizations (i.e. quietly repeating words to themselves as a memory strategy), or otherwise do not count. However, if a participant says a word from the list (e.g. 'parent') out of the context of a recall (e.g. 'My parent shoud be coming to pick me up soon'), *this should be labeled as Off Task*.
9)  **Edits**: *Middle of GUI* There are 3 types of edits that are able to be made here: *Edit*, *Drop*, or *Insert*. To initiate an *Edit* or *Insert*, press *Start Edit/Insert*. Once the start button has been pressed, you can then provide *Time Data* and/or *Word Data*. To Edit the onset/offset of the current row or provide the Insert with the onset/offset, click on the waveform, first, where the onset will be and, second, where the offset will be. For Edits, the red highlighted area over the current word will be updated; for Inserts, a blue highlighted area will be shown on the waveform. Additionally, to Edit the word at the current row or Insert a word, press *Save Edit/Insert* and a text box will appear. Once you press *Continue*, changes will be saved (you can press *Refresh* on the *Left Column* to see your updated changes). Finally, to Drop a row, simply press the *Drop* button.
11)  After finishing all checks on the word, you will press *Next Row* to move on to the next word. 
12)  **Additional Usability**: There's a *Search* button at the *Bottom-Right of GUI* that, once pressed, a text box can be used to search for a specific word or onset (e.g. if the .csv lists 'Curtain' being said at 6.4s, you can type in 'curtain' or 6 and press *Search*). Otherwise, the *Restart*, *Refresh*, *Play Full Audio*, and *Zoom* buttons are pretty self explanatory.
13)  **Progressing** Once finished with a row, press *Next Row* to continue to check the next one. Once finished with a file, text will appear in the *Bottom-Right of GUI* saying 'Press the 'Start' button the begin the next file'. Continue validating until all files in the folder have been validated.

Next Steps:
1) Fix it so you can make an edit and an insert at the same utterance
2) Change it so you can skip to the next file before pressing the start button so you don't have to toggle through every row.
