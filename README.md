PARA RODAR LOCALMENTE

BACK END
pip install -r requirements.txt
.\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload


 
FRONT END
.\venv\Scripts\Activate.ps1
cd frontend
npm install
npm run dev
