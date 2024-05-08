import sqlite3
import tkinter as tk
from tkinter import messagebox,filedialog,simpledialog
from collections import Counter

def veritabanina_baglan_ve_kaydet(text1, text2):
    baglan = sqlite3.connect('metinler.db')
    b = baglan.cursor()

    b.execute('CREATE TABLE IF NOT EXISTS Metinler (id INTEGER PRIMARY KEY, text TEXT)')

    b.execute('DELETE FROM Metinler')

    b.execute('INSERT INTO Metinler (text) VALUES (?)', (text1,))
    b.execute('INSERT INTO Metinler (text) VALUES (?)', (text2,))

    baglan.commit()
    baglan.close()



def metinleri_yukle_ve_karsilastir():
    baglan = sqlite3.connect('metinler.db')
    b = baglan.cursor()
    b.execute('SELECT text FROM Metinler')
    metinler = [text[0].lower() for text in b.fetchall()]
    baglan.close()


    metin1kelimeleri = Counter(metinler[0].split())
    metin2kelimeleri = Counter(metinler[1].split())


    butun_kelimeler = set(metin1kelimeleri).union(metin2kelimeleri)


    intersection = sum(min(metin1kelimeleri[word], metin2kelimeleri[word]) for word in butun_kelimeler)
    total_words = sum(metin1kelimeleri[word] + metin2kelimeleri[word] for word in butun_kelimeler)
    similarity_score = (2.0 * intersection) / total_words if total_words > 0 else 1.0

    return similarity_score


text1 = "Zorluklar başarıya giden yolda sadece adımlardır, vazgeçmek ise yolun sonu demektir"
text2 = "Başarıya giden yolda zorluklar sadece adım adımdır, yolun sonu vazgeçmektir"
veritabanina_baglan_ve_kaydet(text1,text2)


similarity_score = metinleri_yukle_ve_karsilastir()



with open('benzerlik_durumu.txt', 'w') as f:
    f.write(f"Metinler arasındaki benzerlik skoru: {similarity_score:.2f}")


def jaccard_similarite():
    baglan = sqlite3.connect('metinler.db')
    cursor = baglan.cursor()
    cursor.execute('SELECT text FROM Metinler')
    texts = [text[0].lower() for text in cursor.fetchall()]
    baglan.close()

    # Kelimeleri ayırma ve set olarak benzersiz kelimeleri çıkarma
    kelimeler1 = set(texts[0].split())
    kelimeler2 = set(texts[1].split())

    # Kesişim ve birleşim kümelerini bulma
    kesisim = kelimeler1.intersection(kelimeler2)
    birlesim = kelimeler1.union(kelimeler2)

    # Jaccard benzerlik skorunu hesaplama
    if len(birlesim) == 0:
        return 1.0  # Eğer birleşim kümesi boş ise, metinler de boştur ve benzerlik 1.0 olarak kabul edilir.
    similarity_score = 2*(len(kesisim)) / (len(birlesim)+len(kesisim))
    return similarity_score

# Metinleri veritabanına kaydet
text1 = "Zorluklar başarıya giden yolda sadece adımlardır, vazgeçmek ise yolun sonu demektir"
text2 = "Başarıya giden yolda zorluklar sadece adım adımdır, yolun sonu vazgeçmektir"
veritabanina_baglan_ve_kaydet(text1, text2)

# Benzerlik skorunu hesapla ve yazdır
jaccard_score = jaccard_similarite()


with open('benzerlik_durumu.txt', 'a') as f:  # 'a' modu ile dosyaya eklemeyi yaparız
    f.write(f"\nJaccard Benzerlik Skoru: {jaccard_score:.2f}")


# Database connection functions
def veritabani_baglan():
    return sqlite3.connect('uygulama.db')

def kullanici_olustur(kullanici_adi,sifre):
    db = veritabani_baglan()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS kullanicilar (kullanici_adi TEXT,sifre TEXT)")
    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ?",(kullanici_adi,))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO kullanicilar (kullanici_adi,sifre) VALUES (?, ?)",(kullanici_adi, sifre))
    db.commit()
    db.close()
    return True

def kullanici_dogrula(kullanici_adi, sifre):
    db = veritabani_baglan()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (kullanici_adi,sifre))
    user = cursor.fetchone()
    db.close()
    return user is not None

def sifre_degistir(kullanici_adi,yeni_sifre):
    db = veritabani_baglan()
    cursor = db.cursor()
    cursor.execute("UPDATE kullanicilar SET sifre = ? WHERE kullanici_adi = ?",(yeni_sifre,kullanici_adi))
    db.commit()
    db.close()
    messagebox.showinfo("Başarılı","Şifre başarıyla güncellendi!")

# User login and registration class
class KullaniciGiris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kullanıcı Girişi")
        self.geometry("300x150")
        tk.Label(self, text="Kullanıcı Adı:").pack()
        self.kullanici_adi = tk.Entry(self)
        self.kullanici_adi.pack()
        tk.Label(self, text="Şifre:").pack()
        self.sifre = tk.Entry(self,show="*")
        self.sifre.pack()
        tk.Button(self,text="Giriş Yap",command=self.giris_yap).pack()
        tk.Button(self,text="Kayıt Ol",command=self.kayit_ol).pack()

    def giris_yap(self):
        kullanici_adi = self.kullanici_adi.get()
        sifre = self.sifre.get()
        if kullanici_dogrula(kullanici_adi, sifre):
            messagebox.showinfo("Giriş Başarılı","Hoş geldiniz!")
            self.destroy()
            ana_menu(kullanici_adi)
        else:
            messagebox.showerror("Hata","Kullanıcı adı veya şifre yanlış!")

    def kayit_ol(self):
        kullanici_adi = self.kullanici_adi.get()
        sifre = self.sifre.get()
        if kullanici_olustur(kullanici_adi, sifre):
            messagebox.showinfo("Kayıt Başarılı","Kullanıcı oluşturuldu, şimdi giriş yapabilirsiniz.")
        else:
            messagebox.showerror("Hata","Kullanıcı adı zaten mevcut!")

# Main menu and submenu functions
def ana_menu(kullanici_adi):
    menu = tk.Tk()
    menu.title("Ana Menü")
    menu.geometry("200x200")
    tk.Button(menu, text="Karşılaştır",command=lambda: karşılaştırma_penceresi(menu)).pack()
    tk.Button(menu, text="İşlemler",command=lambda: sifre_degistirme_penceresi(kullanici_adi)).pack()
    tk.Button(menu, text="Çıkış",command=menu.quit).pack()
    menu.mainloop()

# Password change functionality
def sifre_degistirme_penceresi(kullanici_adi):
    def submit_new_password():
        yeni_sifre = yeni_sifre_entry.get()
        if yeni_sifre:
            sifre_degistir(kullanici_adi, yeni_sifre)
            sifre_pencere.destroy()

    sifre_pencere = tk.Toplevel()
    sifre_pencere.title("Şifre Değiştirme")
    sifre_pencere.geometry("250x100")
    tk.Label(sifre_pencere,text="Yeni Şifre:").pack()
    yeni_sifre_entry = tk.Entry(sifre_pencere,show="*")
    yeni_sifre_entry.pack()
    tk.Button(sifre_pencere,text="Şifreyi Güncelle",command=submit_new_password).pack()

# Comparison options and text loading
def karşılaştırma_penceresi(parent):
    def execute_comparison():
        try:
            with open(file_path1.get(),'r',encoding='utf-8') as file1, \
                 open(file_path2.get(),'r',encoding='utf-8') as file2:
                text1 = file1.read()
                text2 = file2.read()
            veritabanina_baglan_ve_kaydet(text1, text2)
            if algo_var.get() == "Counter":
                score = metinleri_yukle_ve_karsilastir()
            elif algo_var.get() == "Jaccard":
                score = jaccard_similarite()
            result_label.config(text=f"Benzerlik Skoru: {score:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_file(entry):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    pencere = tk.Toplevel(parent)
    pencere.title("Metin Karşılaştırma")
    pencere.geometry("350x300")

    # Entries for file paths
    tk.Label(pencere, text="Dosya 1:").pack()
    file_path1 = tk.Entry(pencere, width=50)
    file_path1.pack(fill=tk.X, padx=5, pady=5)
    tk.Button(pencere, text="Dosya Seç", command=lambda: select_file(file_path1)).pack()

    tk.Label(pencere, text="Dosya 2:").pack()
    file_path2 = tk.Entry(pencere, width=50)
    file_path2.pack(fill=tk.X, padx=5, pady=5)
    tk.Button(pencere, text="Dosya Seç", command=lambda: select_file(file_path2)).pack()

    algo_var = tk.StringVar(pencere, "Counter")
    tk.Radiobutton(pencere, text="Counter Algoritması", variable=algo_var, value="Counter").pack()
    tk.Radiobutton(pencere, text="Jaccard Algoritması", variable=algo_var, value="Jaccard").pack()

    tk.Button(pencere, text="Karşılaştır", command=execute_comparison).pack()

    result_label = tk.Label(pencere, text="")
    result_label.pack()




if __name__ == "__main__":
    app = KullaniciGiris()
    app.mainloop()




