#para rodar localmente
cd backend
pip install -r requirements.txt  # se ainda não instalou
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev

