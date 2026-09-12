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

# Installation

GossipNet is implemented using a **client-server architecture**.

## Clone the Repository

```bash
git clone https://github.com/Gaurinandana-S/useless_project_GossipNet.git
cd useless_project_GossipNet
```

## Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Install Backend Dependencies

```bash
cd ../backend
pip install -r requirements.txt
```

## Configure Environment Variables

Configure the environment variables using:

```text
.env.example
```

Create the **PostgreSQL database** and configure the database connection.

If Docker is configured for the project:

```bash
docker-compose up -d
```

---

# Run

## Start Backend

From the backend directory:

```bash
uvicorn app.main:app --reload
```

The **FastAPI server** will run locally.

## Start Frontend

From the frontend directory:

```bash
npm run dev
```

Open the **local development URL** shown by Next.js in the terminal.

---

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
