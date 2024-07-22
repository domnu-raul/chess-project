# About

A full-stack web application for playing Chess. The main purpose of this personal project was to familiarize myself with full-stack web development by implementing a small set of features required for this purpose. In order to do this, I have used the following technologies: 
- [PostgreSQL](https://www.postgresql.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- The [Chess](https://python-chess.readthedocs.io/en/latest/) library.
- [VueJS](https://vuejs.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Docker](https://www.docker.com/)

# Features

Although I planned to implement all the minimal features for playing Chess, I also added some other features that I thought would be interesting to implement.
- Authentication(login, register, and sign out)
- Viewing game history
- Viewing user data. On the home page, you can see your details(ELO, victories/defeats/draws), when in-game, you will see the opponent's details.
- Setting a profile picture(includes an editor for cropping to 1:1 ratio)
- Matchmaking.
- ELO system.
- Playing chess. The logic of the game is handled by the Chess library. Forfeiting is possible. Draws and promotions on the front-end are still on the to-do list.
- In-game chat.

# UI
## Authentication
![image](https://github.com/user-attachments/assets/87e24e39-b81e-495b-85e6-9e6e40bd616a)
## Home
![image](https://github.com/user-attachments/assets/c6ce215d-d970-47b8-9c52-2e9c6f04d8bb)
## Chess
![image](https://github.com/user-attachments/assets/2a47d529-4098-4636-8b1b-115d707fe01f)

# User Instructions
- Install Docker.
- Clone the repository.
- From inside the repository, run the following command:
   `docker compose up --build`
