# Image Gallery Project

A full-stack image gallery application built with **Vue 3**, **Vite**, **FastAPI**, **AI**, **Supabase**, and **Axios**.

## Features

* User authentication (signup/login)
* Image upload
* Tagging and search with AI processing
* Real-time gallery display
* Toast notifications with SweetAlert2

---

## Prerequisites

Make sure you have the following installed:

* [Node.js](https://nodejs.org/) v18+
* [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
* [Python](https://www.python.org/) 3.12+
* [pip](https://pip.pypa.io/en/stable/)
* Supabase account for database

---

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/image-gallery.git
cd image-gallery
```

---

### 2. Setup Backend (FastAPI)

1. Navigate to the backend folder:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

* **Windows:**

```bash
.venv\Scripts\activate
```

* **Linux / macOS:**

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file (copy from `.env.example`) and add your Supabase URL and API key:

```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

6. Run the backend locally:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Your backend will be available at `http://127.0.0.1:8000`.

---

### 3. Setup Frontend (Vue 3 + Vite)

1. Navigate to the frontend folder:

```bash
cd ../frontend
```

2. Install dependencies:

```bash
npm install
# or
yarn
```

3. Create a `.env` file (copy from `.env.example`) and add your API URL:

```
VITE_API_URL=http://127.0.0.1:8000
```

4. Run the frontend in development mode:

```bash
npm run dev
# or
yarn dev
```

Your frontend will be available at `http://localhost:4173`.

---

### 4. Building for Production

* **Frontend**:

```bash
npm run build
# or
yarn build
```

* **Preview production build locally**:

```bash
npm run preview
# or
yarn preview
```

---

### 5. Common Issues

* **CORS errors** → make sure your FastAPI backend has CORS enabled for your frontend origin.
* **Dependencies conflicts** → check Python and Node versions.
* **Environment variables not working** → make sure `.env` is created and not tracked by Git.

---

### 6. Scripts

| Command                     | Description                      |
| --------------------------- | -------------------------------- |
| `npm run dev`               | Run frontend in development mode |
| `npm run build`             | Build frontend for production    |
| `npm run preview`           | Preview production build locally |
| `uvicorn main:app --reload` | Run backend in development       |

---

### 7. Notes

* Make sure both backend and frontend are running for full functionality.
* Uploads are stored in Supabase; make sure credentials are valid.
* Use the provided Axios instance for API calls.

  
## AI Integration: Hugging Face vs OpenAI
This project leverages Hugging Face for AI/ML tasks such as image tagging, text analysis, or embeddings. Initially, OpenAI was considered, but Hugging Face was chosen for this project.

* Why Hugging Face over OpenAI
---

| Factor                      | Hugging Face                                                                                 | OpenAI                                         |
| --------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **Model Availability**      | Extensive library of pre-trained models (transformers, text, vision, audio) with open access | Closed models; GPT and DALL-E primarily        |
| **Cost**                    | Free tier with generous usage limits, pay-as-you-go for hosted Inference API                 | Paid only, with lower free quota               |
| **Customizability**         | Easy to fine-tune or deploy custom models                                                    | Limited fine-tuning options; mostly API access |
| **Self-Hosting**            | Models can be downloaded and run locally, reducing API costs and latency                     | API-only; cannot self-host GPT models          |
| **Community & Open Source** | Strong open-source community, many contributions and pre-trained models                      | Proprietary, limited open-source models        |
| **Privacy**                 | Data can stay on your servers if you self-host                                               | All API calls go through OpenAI servers        |



* Cost Comparison (as of 2025)
---

| Provider     | Free Tier                        | Paid Tier                                  | Notes                                        |
| ------------ | -------------------------------- | ------------------------------------------ | -------------------------------------------- |
| Hugging Face | 30k requests/month on hosted API | $0.01–$0.10 per request depending on model | Can self-host free of cost                   |
| OpenAI       | $5 free credit                   | $0.03–$0.12 per 1k tokens (GPT models)     | No self-hosting; data sent to OpenAI servers |

---

## 🚀 Potential Improvements

Here are some ideas to further enhance this project:

### Frontend (Vue.js / Vite)
- Implement **infinite scrolling** or lazy-loading for gallery images.
- Enhance search with **multi-tag search**, **filters by color, date, or user**, and AI-based **search suggestions**.
- Expand the **Toast/notification system** for errors, warnings, and updates.

### Backend (FastAPI / Supabase)
- Switch to **JWT-based authentication** for better security.
- Add **rate-limiting** and validate uploaded images for type/size.
- Implement **bulk image upload and tag update** endpoints.
- Enable **AI-based auto-tagging** and **image similarity search**.
- Add **role-based access control** (admin vs regular users).
- Optimize database with **indexes** and **thumbnail storage** for faster queries.

> These improvements can help make the platform more robust, user-friendly, and scalable.

### Demo video
[Watch the demo video](https://drive.google.com/file/d/18PxisfhviLGNOxsOvqds_JqRRVrROU-C/view)
