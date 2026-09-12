<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# GossipNet 🎯

## Basic Details

### Team Name

**Solastice**

### Team Members

* **Team Lead:** Gaurinandana S — RIT Kottayam

---

## Project Description

**GossipNet** is an interactive deduction game that models family gossip as a social graph. Players investigate a dynamically expanding family network through a chatbot, uncover relationships and behavioral clues, and attempt to identify the person responsible for starting a fictional rumor.

Behind the ridiculous premise is a legitimate graph-based system involving **relationship modeling, graph traversal, dynamic graph generation, information propagation, and progressive investigation**.

---

## The Problem (that doesn't exist)

Every family has important unanswered questions:

* **Who started the rumor?**
* Who told whom?
* Why does everyone know except you?
* How did a completely harmless piece of information reach three different households in 20 minutes?
* And most importantly... **who started it?**

Traditional software has completely failed to solve this extremely serious problem.

There is therefore an urgent need for a **sophisticated system capable of investigating family gossip networks.**

---

## The Solution (that nobody asked for)

GossipNet turns family gossip into a **graph investigation game**.

The player investigates family members through a conversational chatbot while exploring a dynamically expanding family/social graph.

### Players can investigate:

* **Generation**
* **Age**
* **Family relationships**
* **Households**
* **Previous rumors**
* **Gossip reputation**
* **Trust**
* **Suspicious relationships**
* **Social connections**
* **Information flow**

The graph progressively expands as the player makes guesses, revealing deeper levels of the family and introducing new suspects.

And when the player finally gets the answer:

> **"You were right. Unfortunately, you're wrong."**

Because apparently even being correct isn't allowed to be satisfying.

---

# Technical Details

## Technologies / Components Used

### For Software

#### Languages Used

* **Python**
* **TypeScript**
* **JavaScript**
* **SQL**
* **HTML**
* **CSS**

#### Frameworks

* **Next.js**
* **React**
* **FastAPI**

#### Libraries

* **React Flow**
* **NetworkX**
* **Pydantic**
* **SQLAlchemy**
* **PostgreSQL client libraries**
* **Tailwind CSS**

#### Tools

* **Git**
* **GitHub**
* **Visual Studio Code**
* **Docker / Docker Compose**
* **Postman / API testing tools**

### For Hardware

No specialized hardware is required.

GossipNet is a **software-only application** and can run on a standard laptop or desktop computer.

---

# Implementation

## Architecture

GossipNet is implemented using a **client-server architecture**.

### Frontend

The frontend is built using **Next.js, React, and TypeScript**.

The main interface consists of:

* **Interactive family/social graph**
* **Chat-based interrogation panel**
* **Rumor information panel**
* **Investigation controls**
* **Guess system**
* **Floating "Give Up, Bro" button**
* **Score and game statistics**
* **Result screen**

The graph is rendered using **React Flow**, allowing users to:

* Pan
* Zoom
* Select people
* Navigate large graphs
* View relationship edges
* Observe newly revealed family members

---

### Backend

The backend uses **FastAPI and Python**.

It manages:

* **Game state**
* **Family graph generation**
* **Relationship calculations**
* **Rumor generation**
* **Investigation questions**
* **Graph revelation**
* **Guess validation**
* **Scoring**
* **Game progression**

---

### Graph Engine

**NetworkX** is used to represent the family/social network.

The graph contains:

* **People as nodes**
* **Family relationships as edges**
* **Social relationships as edges**
* **Multiple households**
* **Multiple generations**
* **Friends**
* **Neighbors**
* **Colleagues**
* **In-laws**

The backend maintains the **complete graph** while exposing only the appropriate portion to the player.

---

## Dynamic Investigation

The player initially sees only a **small section of the graph**.

The player can interrogate revealed people through the chatbot.

Questions produce useful clues and allow the player to make deductions.

When a player makes an **incorrect guess**, the family graph expands **downward**, revealing another level of the family.

This creates a progressive investigation experience:

```text
Investigate
     ↓
Gather clues
     ↓
Guess
     ↓
Wrong
     ↓
Family tree expands
     ↓
New people appear
     ↓
Investigate again
     ↓
Guess again
```

---

## Guess System

Players can make an **unlimited number of guesses**.

After the **first guess**, the **"Give Up, Bro"** button becomes available.

The button remains visible as a **floating action** until the player presses it.

### A wrong guess:

* Does **not** end the game
* Produces a humorous response
* Expands the family tree
* Allows the player to continue investigating

### A correct guess:

Ends the round but displays an intentionally confusing result message.

> **You were right.**
>
> **Unfortunately, you're wrong.**
>
> *We're investigating.*

---

## New Round Generation

Every new round generates a completely new:

* **Family graph**
* **People**
* **Households**
* **Relationships**
* **Social connections**
* **Rumor**
* **Rumor subject**
* **Rumor starter**

The graph is generated using **deterministic random seeds** so that game states can be reproduced for testing.

---

# Installation & Local Setup

GossipNet uses a **client-server architecture** consisting of a Next.js frontend, FastAPI backend, and PostgreSQL database.

## Prerequisites

Make sure the following are installed:

* **Git**
* **Node.js and npm**
* **Python 3.x**
* **PostgreSQL**
* **Docker / Docker Compose** *(if using the provided Docker configuration)*

---

## 1. Clone the Repository

```bash
git clone https://github.com/Gaurinandana-S/useless_project_GossipNet.git
cd useless_project_GossipNet
```

---

## 2. Start the Database

If the project is configured with Docker Compose, start the required services using:

```bash
docker-compose up -d
```

Check the running containers:

```bash
docker-compose ps
```

Make sure the PostgreSQL service is running before starting the backend.

---

## 3. Configure the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

### Windows

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Configure the required environment variables using the project's `.env.example` file.

Make sure the PostgreSQL database connection details are correctly configured.

---

## 4. Start the Backend

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The FastAPI backend will start at:

**http://127.0.0.1:8000**

FastAPI's interactive API documentation is available at:

**http://127.0.0.1:8000/docs**

---

## 5. Start the Frontend

Open a **new terminal window** and navigate to the frontend:

```bash
cd frontend
```

Install the Node.js dependencies:

```bash
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

The frontend will be available at:

**http://localhost:3000**

Open this URL in your browser to start playing GossipNet.

---

## Running the Complete Application

GossipNet requires the following components to be running:

```text
                 ┌──────────────────────┐
                 │      User Browser     │
                 │   http://localhost:3000
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Next.js Frontend   │
                 │   React + TypeScript │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    FastAPI Backend   │
                 │   http://127.0.0.1:8000
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     PostgreSQL       │
                 │       Database       │
                 └──────────────────────┘
```

### Terminal 1 — Database

```bash
docker-compose up -d
```

### Terminal 2 — Backend

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Terminal 3 — Frontend

```bash
cd frontend
npm run dev
```

Then open:

**http://localhost:3000**

---

## Troubleshooting

### Backend does not start

Make sure the virtual environment is activated and dependencies are installed:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

Then run:

```bash
uvicorn app.main:app --reload
```

### Frontend dependencies are missing

From the `frontend` directory:

```bash
npm install
```

Then:

```bash
npm run dev
```

### PostgreSQL connection error

Make sure the database service is running:

```bash
docker-compose ps
```

Also verify the database credentials and connection URL in the backend environment configuration.

### Port already in use

If port `3000` is already being used, Next.js will automatically offer another available port.

If port `8000` is already being used, start FastAPI on another port:

```bash
uvicorn app.main:app --reload --port 8001
```

Make sure the frontend is configured to communicate with the updated backend URL.


# Project Documentation

The project documentation covers:

* **System architecture**
* **Family/social graph model**
* **Graph generation**
* **Relationship engine**
* **Dynamic graph revelation**
* **Chatbot investigation system**
* **Rumor generation**
* **Guess mechanics**
* **Scoring**
* **API architecture**
* **Database structure**
* **Testing**
* **Future expansion**

---

# Screenshots

## Home Page

![GossipNet Home Page](images/Screenshot\(14\).png)

## Game Screen — Phase 1

![GossipNet Phase 1](images/Screenshot\(15\).png)

## Result Screen — Phase 1

![GossipNet Phase 1 Result](images/Screenshot\(16\).png)

## Game Screen — Phase 2

![GossipNet Phase 2](images/Screenshot\(17\).png)

## Result Screen — Phase 2

![GossipNet Phase 2 Result](images/Screenshot\(18\).png)

---

# Deployment

### Vercel Deployment Link

**Add your Vercel deployment link here.**

---

# Project Demo

## Video

**Add your demo video link here.**

The video demonstrates the core gameplay, investigation process, graph expansion, guessing mechanics, and final result.

---

## Made with ❤️ at TinkerHub Useless Projects

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000\&link=https%3A%2F%2Fwww.tinkerhub.org%2F)

![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)
