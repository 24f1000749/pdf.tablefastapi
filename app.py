from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()

    total_sum = 0.0

    with open("temp.pdf", "wb") as f:
        f.write(contents)

    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                headers = [str(h).strip().lower() if h else "" for h in table[0]]

                # Find important columns
                gadget_col = None
                total_col = None

                for i, h in enumerate(headers):
                    if "item" in h or "product" in h or "name" in h:
                        gadget_col = i
                    if "total" in h:
                        total_col = i

                if gadget_col is None or total_col is None:
                    continue

                for row in table[1:]:
                    if not row:
                        continue

                    try:
                        item = str(row[gadget_col]).strip()

                        if item.lower() == "gadget":
                            value = str(row[total_col])

                            # remove ₹, commas etc
                            value = re.sub(r"[^0-9.]", "", value)

                            if value:
                                total_sum += float(value)
                    except:
                        pass

    # if sum is whole number, return int
    if total_sum.is_integer():
        total_sum = int(total_sum)

    return {"sum": total_sum}
