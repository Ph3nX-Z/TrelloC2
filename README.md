# TrelloC2
C2 over Trello

<img width="848" height="461" alt="image" src="https://github.com/user-attachments/assets/036685b0-6637-4c35-96c3-a60a71daefc6" />

## Usage

1. Create a board and get the board id
2. Generate an API key using trello (see doc)
3. Use this call to get a non expiring token : https://trello.com/1/connect?key=yourkey&name=your_board_name&expiration=never&response_type=token&scope=read,write
4. Fill the token and the board id in the agent.nim template, and change the password for encryption
5. Install libraries for the agent (nimble install)
6. Compile it in no console mode, under windows : nim --app:gui c agent.nim, under linux : nim --app:gui -d:mingw c agent.nim
7. Use the CLI tool as explained in the help mode:
   
<img width="829" height="538" alt="image" src="https://github.com/user-attachments/assets/b4f6ce0d-c00d-4e05-8b9d-6398980cd716" />

Your C2 is now ready to use :) 
