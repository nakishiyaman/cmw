# Blog API - Requirements

## 1. Overview
Blog API with user authentication

## 2. Tech Stack
- Backend: FastAPI
- Database: SQLite3
- Auth: JWT

## 3. Data Models
### User
- id, username, email, password

### Post
- id, title, content, author_id

## 4. API Features
### Authentication
- POST /auth/register
- POST /auth/login

### Posts
- GET /posts
- POST /posts
- PUT /posts/{id}
- DELETE /posts/{id}
