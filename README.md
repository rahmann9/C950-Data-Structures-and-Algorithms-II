# Package Delivery Optimization Project

## 🚀 Project Overview
This project simulates a real-world package delivery system. You'll develop a logistics application that optimizes truck routes and manages packages under specific constraints using a custom-built hash table and a route-planning algorithm. The objective is to ensure that all packages are delivered on time and the total mileage for all trucks does not exceed 140 miles.

## 🧰 Setup Instructions

### 1. Environment Setup
- Install [Python](https://www.python.org/downloads/)
- Install [PyCharm IDE](https://www.jetbrains.com/pycharm/download/?section=mac) (or use IntelliJ/Xcode if preferred)

### 2. Download Required Files
Obtain the following project files:
- Distance Table
- Project Implementation Steps
- Task Templates (ensure version matches your rubric)
- Any additional documentation listed with your rubric

---

## 📝 Project Summary

- You’ll manage up to **3 trucks** and **2 drivers**
- **Maximum combined mileage:** 140 miles
- **Truck speed:** 18 mph
- **Truck capacity:** 16 packages
- Package constraints include:
  - One has a wrong address updated at **10:20am**
  - A group of **6 packages must be delivered together**
  - Certain packages must be delivered **by 10:30am**
- Trucks can return to the hub to reload
- No stopping for fuel or breaks

---

## 🔍 Core Tasks Overview

### Task 1: Planning and Documentation

#### ✅ Requirements:
- Define a self-adjusting hash table (no dictionaries allowed)
- Select and explain a routing algorithm (e.g., Nearest Neighbor, 2-opt)
- Write pseudocode and analyze time complexity
- Identify and explain data structures used and their tradeoffs
- Justify choices for maintainability, efficiency, and scalability

---

### Task 2: Implementation

#### ✅ Key Steps:
1. **Build a Custom Hash Table**
   - Support insert and lookup operations
   - Handle collisions and resizing dynamically

2. **Load Package Data**
   - Clean and import the package CSV
   - Convert records into class instances and insert into the hash table

3. **Create a Truck Class**
   - Manage route, start time, capacity, and delivery logic

4. **Implement a Routing Algorithm**
   - Optimize delivery sequence
   - Ensure all constraints and time requirements are met

5. **Parse Distance Matrix**
   - Store in a structure like a 2D list or hash map
   - Support mirrored distance lookups if needed

6. **User Interface**
   - Provide a command-line interface with options to:
     - Look up a single package by ID and time
     - View all package statuses at a specific time
     - Display mileage and route summary

---

## 📊 Interface Features
- Simple CLI for package and route queries
- Validates and formats time input
- Three core reports:
  - View all packages at a specified time
  - Look up a package by ID and time
  - View truck summary including routes and mileage

---

## 📌 Reflections & Final Notes

- Reflect on:
  - Strengths and limitations of your algorithm
  - How the hash table supported the project goals
  - Improvements you’d make in a future implementation

- Include:
  - APA-style citations for external references
  - Screenshots of key features and logic:
    - Hash table implementation
    - Routing algorithm
    - CLI interface and output
    - Mileage and delivery verification
