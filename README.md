# whatstatone

This program uses backup .txt files from whatsapp to build animated bar charts of people
that exchanged more messages and words with you. This program can be run in Linux and Mac OS directly. Users of Windows
need to edit the lines in the program that paths are used (change for exemple foo/bar to foo\\bar) .

How it works

- Use the export option in WhatsApp to export the .txt of your chats. You can choose "without media" to make it quicker. 
- Rename the files with nice names. It will be used to label the bar chart. Do not use names with over 50 characters. 
- Put all exported .txt files inside a folder named "msg" in the *same directory where main.py is* !
- Run main.py 
