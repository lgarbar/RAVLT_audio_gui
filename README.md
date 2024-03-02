# Ravlt Audio Gui

In this folder, you'll find a
1) environment.txt or environment.yml (should be interchangeable for our purposes) which lists all the dependencies needed for this project. You can make a new conda environment using:
```bash
conda create --name my_environment --file req.txt
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

3) After launching the code, a dialog box prompting the user to input their initials. This is just to keep of making edits and where.
4) After pressing 'Submit', a GUI will appear.
5) **Importing Data**: Press *Import* to import a partcipant folder listing the audio transcriptions. You'll see a window showing the current directory: click on the folder named RAVLT, then the participant’s folder that you want to score. You should then see the name of the entire directory for that folder in the textbox at the bottom of the window.
6) **Getting Started**: Once imported, you'll see 2 other windows populate: the *Top Left* displays the .csv as edits are made; the *Top Right* displays the waveform for the audio (this will be necessary for making *Edits* and *Inserts* (see below).
7) The name of the current block (e.g. Block 1 Recall) will apppear in the *Left Column*. Once ready to begin, press *Start* and the current word will appear at the bottom of the *Middle Column* as well as be highlighted in the *Top Left* window. *Recommended*: We recommend, for any given block, to press *Play Full Audio* and listen to/make notes of all utterances. The reason for this is that the auto-transcription will sometimes miss utterances completely or overlap them with marked words and these misses will be impossible to see by simply listening to each marked utterance. Additionally, it feels a bit more efficient since you will already have an idea of where to make edits and won't have to listen to every single utterance. You can press *Play Audio Segment* to play the audio for any given line, however.
9)  **Quality Check**: *Bottom Right of GUI* Once the audio plays, the *first* thing we want to check if the speech was correctly transcribed. You do this by pressing *Accept* to validate the transcription, *For Review* for audio that may be inaudible or otherwise difficult to understand, and *Off Task* for any speech that was not an attempt to recall a word from the list (e.g. 'I'm tired', 'My parent shoud be coming to pick me up soon'). Additionally, you can press *Add Note* to add any information about a decision related to the quality check or edits.
10)  *Important Note*: For an utterance to qualify as *Off Task*, it must not relate at all to the task. Any repeats, mistakes (e.g. says 'drape' rather than 'curtain'), subvocalizations (i.e. quietly repeating words to themselves as a memory strategy), or otherwise should not be marked as *Off Task* **since those relate to the task**. However, if a participant says a word from the list (e.g. 'parent') out of the context of a recall (e.g. 'My parent shoud be coming to pick me up soon'), **this should be labeled as Off Task**.
11)  **Edits**: *Middle of GUI* There are 3 types of edits that are able to be made here: *Edit*, *Drop*, or *Insert*. To initiate an *Edit* or *Insert*, press *Start Edit/Insert*. Once the start button has been pressed, a popup window will appear when you can type in the edit/insert you want to make (**Note**: you do not *have* to type in anything when making an edit if you're only changing the *Time Data*). After pressing *Continue*, you can then provide *Time Data*. To Edit the onset/offset of the current row or provide the Insert with the onset/offset, click on the waveform, first, where the onset will be and, second, where the offset will be. For Edits, the red highlighted area over the current word will be updated; for Inserts, a blue highlighted area will be shown on the waveform. Next, press *Save Edit/Insert* and all changes will be saved (you can press *Refresh* on the *Left Column* to see your updated changes). Finally, to Drop a row, simply press the *Drop* button.
12)  After finishing all checks on the word, you will press *Next Row* to move on to the next word. 
13)  **Additional Usability**: There's a *Search* button at the *Bottom-Right of GUI* that, once pressed, a text box can be used to search for a specific word or onset (e.g. if the .csv lists 'Curtain' being said at 6.4s, you can type in 'curtain' or 6 and press *Search*). Otherwise, the *Restart*, *Refresh*, *Play Full Audio*, and *Zoom* buttons are pretty self explanatory.
14)  **Progressing** Once finished with a row, press *Next Row* to continue to check the next one. Once finished with a file, text will appear in the *Bottom-Right of GUI* saying 'Press the 'Start' button the begin the next file'. Continue validating until all files in the folder have been validated.
