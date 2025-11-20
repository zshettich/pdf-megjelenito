# HZS PDF Explorer

## Hallgató
Név: Hettich Zsolt  
Neptunkód: ZAJDU4  

---

## Feladat leírása
Ez az alkalmazás egy modern, **Windows 11-szerű ** grafikus felületű **PDF-fájlkezelő és -megjelenítő**.  
A program a bal oldalon fájlrendszer-fát jelenít meg, a jobb oldalon pedig a kiválasztott PDF-dokumentumot.  
A felhasználó lapozhat az oldalak között, nagyíthat, kicsinyíthet, illetve visszaállíthatja az eredeti nézetet.  
A felső eszköztárban keresőmező is található, amellyel PDF-fájlokat lehet szűrni név alapján.

A feladat célja egy tanult és bemutatandó modulokra épülő, saját modult is tartalmazó, eseményvezérelt grafikus Python-alkalmazás létrehozása volt.

---

## Modulok és a modulokban használt függvények

### Tanult modulok:
- **os** – fájl- és útvonalkezelés (`path`, `isfile`, `basename`)
- **sys** – programindítás kezelése
- **PySide6.QtWidgets**, **PySide6.QtGui**, **PySide6.QtCore** – grafikus felület, eseménykezelés  
  - `QApplication()`, `QMainWindow()`, `QFileSystemModel()`, `QTreeView()`, `QSplitter()`,  
    `QLabel()`, `QPushButton()`, `QScrollArea()`, `QToolBar()`, `QAction()`
  - `Qt.AlignCenter`, `QPixmap()`, `QImage()`
- **QDir** – könyvtárak, meghajtók listázása
- **QStyle** – rendszerikonok használata (Windows-stílushoz)
- **QLineEdit** – keresőmező eseménykezelése (`textChanged`)

### Bemutatandó modul:
**fitz (PyMuPDF)** – PDF megjelenítéshez  
- `fitz.open(path)` – PDF megnyitása  
- `page.get_pixmap(matrix=...)` – PDF oldal képként való renderelése  
- `fitz.Matrix()` – nagyítás és kicsinyítés kezelése  

### Saját modul:
**hzs_utils.py** – Főmodul a HZS monogrammal  
- Tartalmazza a `HZSFileHelper` osztályt és a `hzs_format_path()` függvényt

---

## Osztály(ok)

### **HZSFileHelper**
Saját osztály, amely a fájlnevek és útvonalak kezelését végzi.
- `hzs_is_pdf(path)` – Ellenőrzi, hogy a megadott fájl PDF-e  
- `hzs_filename(path)` – A fájlnév kinyerése az útvonalból  

### **PDFViewer (main.py)**
A fő grafikus osztály, amely tartalmazza:
- A teljes GUI felépítését (bal oldali fájlfa, jobb oldali PDF megjelenítő)
- Toolbar gombokat (lapozás, zoom, reset)
- Eseménykezelést (kattintás, keresés, zoom)
- PDF renderelést (`fitz` modul segítségével)

---

## Saját függvények (HZS előtaggal)
- **`hzs_format_path(path, max_len=60)`**  
  Rövidíti a hosszú fájlútvonalakat megjelenítéshez, a közepét `...` jellel helyettesítve.  
  A funkció a státuszsorban és a fájlnév megjelenítésénél használatos.

---

## Indításhoz szükséges modulok
- **PySide6** – GUI keretrendszer  
- **PyMuPDF (fitz)** – PDF megjelenítés  
Telepítés:
```bash
pip install PySide6 pymupdf
