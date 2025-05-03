# Big Red Beli 

Rate and share your favorite spots on campus with friends! 😋

### Authors 🧑‍💻
Backend: Cam Keller, Claire Yu, Lydia Shen

iOS: Parsa Tehranipoor 

### [iOS repo](https://github.com/parsa-tehranipoor/hack-challenge-frontend) 📇

## Description 
A Beli-style social media app for reviewing food at Cornell dining locations. Users can rank and review spots they’ve tried, follow friends, and view friends' reviews in order to inform their next bite! Competitive eaters can increase their campus-wide ranking by reviewing more and more spots.

## Backend
***Routes***
- **GET**: 
    - User: get all users, get a user, get user followers, get user following, get user reviews, get user's following's reviews, get user ranking, get user average rating, get user rating count
    - Connection: get all connections, get a connection
    - Eatery: get all eateries, get an eatery, get eatery reviews, get eatery average rating
    - Review: get all reviews, get a review
- **POST**:
    - User: create user
    - Connection: follow (create connection)
    - Eatery: create eatery
    - Review: create review
- **DELETE**:
    - User: delete user
    - Connection: unfollow (delete connection)
    - Eatery: delete eatery
    - Review: delete review
- **PUT**:
    - Review: edit review

***Tables + Relationships***
- **User**: represents users
    - Many-to-many relationship with Connection
    - One-to-many relationship with Review
- **Connection**: represents connections (follows) between users
    - Many-to-many relationship with User
- **Eatery**: represents campus eateries
    - One-to-many relationship with Review
- **Review**: represents reviews made by users for specific eateries
    - Many-to-one relationship with User
    - Many-to-one relationship with Eatery

***API spec***

Click [here](https://docs.google.com/document/d/1cvVmiNQGCx-TmkB7CeLi_-prxknVP0Kliv7s0KwlAjI/edit?usp=sharing) to view our API spec!


<!-- ***Explanation of database & API design***
<img width="1125" alt="Screenshot 2025-04-29 at 11 52 48 PM" src="https://github.com/user-attachments/assets/54e20856-096b-45ae-b4e9-18a6cb287e3f" />

<img width="1116" alt="Screenshot 2025-04-29 at 11 53 05 PM" src="https://github.com/user-attachments/assets/eed39566-ff5b-446c-a24c-96bb92df0c76" /> -->
