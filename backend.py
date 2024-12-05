import tkinter as tk
import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate(r'auth_key.json')
firebase_admin.initialize_app(cred)


db = firestore.client()

def store_data(name, rating, comments):
    doc_ref = db.collection('user_feedback').document()
    data = {
        'name': name,
        'rating': rating,
        'comments': comments
    }
    try:
        doc_ref.set(data)
        print("Data saved successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

def submit_data():
    name = name_entry.get()
    rating = rating_entry.get()
    comments = comments_text.get("1.0", tk.END).strip()

    if not name or not rating or not comments:
        print("Please fill out all fields")
        return

    store_data(name, rating, comments)

root = tk.Tk()

tk.Label(root, text="Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Rating").pack()
rating_entry = tk.Entry(root)
rating_entry.pack()

tk.Label(root, text="Comments").pack()
comments_text = tk.Text(root, height=5, width=30)
comments_text.pack()

submit_button = tk.Button(root, text="Submit", command=submit_data)
submit_button.pack()

root.mainloop()
