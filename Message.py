import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import tkintermapview
import requests

# Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(r'auth_key.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()


def reverse_geocode(lat, lon):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'lat': str(lat),
        'lon': str(lon),
        'format': 'jsonv2',
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'Codebreaker Map (justmezavierj@gmail.com)'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def forward_geocode(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'jsonv2',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {
        'User-Agent': 'Codebreaker Map (justmezavierj@gmail.com)'  # Replace with your app name and contact info
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return float(lat), float(lon)
    else:
        return None


class MapDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Mappy')
        self.root.geometry("1300x700")
        self.marker_mapping = {}  # doc to marker
        self.markers = {}  # marker to doc

        # GUI setup
        self.root.columnconfigure(0, weight=3, uniform="equal")  # map columns
        self.root.columnconfigure(1, weight=2, uniform="equal")  # controls columns
        self.root.rowconfigure(0, weight=1, uniform="equal")

        # Map frame
        self.map_frame = tk.Frame(self.root)
        self.map_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.map_widget = tkintermapview.TkinterMapView(
            self.map_frame, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(41.620456, -93.601054)  # starting position
        self.map_widget.set_zoom(16)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # Right click event binder
        self.map_widget.canvas.bind("<Button-3>", self.map_right_click_event)

        # Control frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Add/Edit/Remove buttons
        self.add_button = tk.Button(self.control_frame, text="Add Destination", font="Arial 11 bold", width=20,
                                    command=self.add_destination)
        self.add_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.edit_button = tk.Button(self.control_frame, text="Edit Destination", font="Arial 11 bold", width=20,
                                     command=self.edit_destination)
        self.edit_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.remove_button = tk.Button(self.control_frame, text="Remove Destination", font="Arial 11 bold", width=20,
                                       command=self.remove_destination)
        self.remove_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Data treeview
        tk.Label(self.control_frame, text="Stored Pins:", font="Arial 11 bold").grid(row=3, column=0, sticky="w",
                                                                                     padx=5, pady=5)

        # Treeview creator
        self.data_treeview = ttk.Treeview(self.control_frame)
        self.data_treeview.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

        # Columns
        self.data_treeview['columns'] = ('Address',)
        self.data_treeview.column('#0', width=150, anchor='w')  # '#0' is the tree column (for 'name')
        self.data_treeview.column('Address', width=250, anchor='w')

        # Headers
        self.data_treeview.heading('#0', text='Name', anchor='w')
        self.data_treeview.heading('Address', text='Address', anchor='w')

        # Fetch and display data on startup
        self.fetch_and_display_data()

        self.control_frame.grid_rowconfigure(4, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)

    def add_destination(self):

        self.open_form_window()

    def edit_destination(self):

        selected_item = self.data_treeview.selection()
        if selected_item:
            doc_id = selected_item[0]  # iid= doc id
            self.open_form_window(doc_id=doc_id)
        else:
            messagebox.showwarning("No Selection", "Please select a destination to edit.")

    def remove_destination(self):

        selected_item = self.data_treeview.selection()
        if selected_item:
            doc_id = selected_item[0]
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this destination?")
            if confirm:
                self.remove_destination_by_id(doc_id)
        else:
            messagebox.showwarning("No Selection", "Please select a destination to remove.")

    def map_right_click_event(self, event):
        widget = event.widget
        if widget != self.map_widget.canvas:
            return

        # Get coordinates from click
        x, y = event.x, event.y
        lat, lon = self.map_widget.convert_canvas_coords_to_decimal_coords(x, y)

        try:
            address_info = reverse_geocode(lat, lon)
            address = address_info.get('address', {})

            # Address components
            house_number = address.get('house_number', '')
            road = address.get('road', '')
            city = address.get('city') or address.get('town') or address.get('village', '')
            postcode = address.get('postcode', '')

            # Construct address text
            address_parts = [part for part in [house_number, road, city] if part]
            if postcode:
                address_parts.append(f"({postcode})")
            address_text = ", ".join(address_parts)

        except Exception as e:
            print(f"Error during reverse geocoding: {e}")
            address_text = "Unknown Location"

        # Fill form on edit
        self.open_form_window(lat=lat, lon=lon, address=address_text)

    def marker_click_event(self, marker):

        doc_id = self.markers.get(marker)
        if doc_id:
            self.open_form_window(doc_id=doc_id)
        else:
            messagebox.showerror("Error", "Marker not associated with any data.")

    def open_form_window(self, doc_id=None, lat=None, lon=None, address=None):
        form_window = tk.Toplevel(self.root)
        form_window.title("Destination Form")

        # modal
        form_window.transient(self.root)  #
        form_window.grab_set()

        #  definitions
        def submit():
            name = name_entry.get()
            address = address_entry.get()
            rating = rating_entry.get()
            comments = comments_text.get("1.0", tk.END).strip()

            if not name or not address or not rating or not comments:
                messagebox.showwarning("Incomplete Data", "Please fill out all fields.")
                return

            if doc_id:
                # Update existing entry
                self.store_data(name, address, rating, comments, lat, lon, doc_id=doc_id)
            else:
                # Add new entry
                self.store_data(name, address, rating, comments, lat, lon)

            form_window.destroy()

        def delete():
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this destination?")
            if confirm and doc_id:
                self.remove_destination_by_id(doc_id)
                form_window.destroy()

        # GUI elements
        tk.Label(form_window, text="Name of Place").grid(row=0, column=0, sticky='e')
        name_entry = tk.Entry(form_window)
        name_entry.grid(row=0, column=1)

        tk.Label(form_window, text="Address").grid(row=1, column=0, sticky='e')
        address_entry = tk.Entry(form_window)
        address_entry.grid(row=1, column=1)

        tk.Label(form_window, text="Rating (1-5)").grid(row=2, column=0, sticky='e')
        rating_entry = tk.Entry(form_window)
        rating_entry.grid(row=2, column=1)

        tk.Label(form_window, text="Comments").grid(row=3, column=0, sticky='ne')
        comments_text = tk.Text(form_window, height=5, width=30)
        comments_text.grid(row=3, column=1)

        # Pre-fill form if editing an existing entry
        if doc_id:
            # Edit existing entry
            doc_ref = db.collection('user_feedback').document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                name_entry.insert(0, data['name'])
                address_entry.insert(0, data['address'])
                rating_entry.insert(0, data['rating'])
                comments_text.insert('1.0', data['comments'])
                lat = data.get('latitude')
                lon = data.get('longitude')
            else:
                messagebox.showerror("Error", "Document does not exist.")
                form_window.destroy()
                return
        else:
            # Add new entry
            if address:
                address_entry.insert(0, address)

        # Buttons
        submit_button = tk.Button(form_window, text="Submit", command=submit)
        submit_button.grid(row=4, column=0, pady=10)

        if doc_id:
            delete_button = tk.Button(form_window, text="Delete", command=delete)
            delete_button.grid(row=4, column=1, pady=10)

            submit_button = tk.Button(form_window, text="Submit", command=submit)
            submit_button.grid(row=4, column=0, pady=10)

            if doc_id:
                delete_button = tk.Button(form_window, text="Delete", command=delete)
                delete_button.grid(row=4, column=1, pady=10)

    def store_data(self, name, address, rating, comments, lat, lon, doc_id=None):
        if doc_id:
            # Updating an existing entry
            doc_ref = db.collection('user_feedback').document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                current_data = doc.to_dict()
                current_address = current_data.get('address')
                if current_address != address:
                    # Address has changed, geocode new coordinates
                    print("Address changed, geocoding new coordinates...")
                    try:
                        position = forward_geocode(address)
                        if position:
                            lat, lon = position
                        else:
                            messagebox.showerror("Geocoding Error", f"Could not geocode the address: {address}")
                            return
                    except Exception as e:
                        print(f"Error during forward geocoding: {e}")
                        messagebox.showerror("Geocoding Error", f"An error occurred during geocoding: {e}")
                        return
        else:
            # Adding a new entry
            if lat is None or lon is None:
                # Geocode the address to get coordinates
                try:
                    position = forward_geocode(address)
                    if position:
                        lat, lon = position
                    else:
                        messagebox.showerror("Geocoding Error", f"Could not geocode the address: {address}")
                        return
                except Exception as e:
                    print(f"Error during forward geocoding: {e}")
                    messagebox.showerror("Geocoding Error", f"An error occurred during geocoding: {e}")
                    return

        # Proceed to save data and place marker
        doc_ref = db.collection('user_feedback').document(doc_id) if doc_id else db.collection(
            'user_feedback').document()

        # Remove old marker if updating
        if doc_id and doc_id in self.marker_mapping:
            old_marker = self.marker_mapping[doc_id]
            old_marker.delete()
            del self.marker_mapping[doc_id]
            del self.markers[old_marker]

        # Saving new data to document
        data = {
            'name': name,
            'address': address,
            'rating': rating,
            'comments': comments,
            'latitude': lat,
            'longitude': lon
        }
        try:
            doc_ref.set(data)
            print(f"Storing data: Name={name}, Address={address}, Lat={lat}, Lon={lon}, DocID={doc_id}")
            # Placing marker on the map
            new_marker = self.map_widget.set_marker(
                lat, lon, text=name, command=lambda: self.marker_click_event(new_marker))
            self.marker_mapping[doc_ref.id] = new_marker
            self.markers[new_marker] = doc_ref.id

            # Refreshing display
            self.fetch_and_display_data()
        except Exception as e:
            print(f"An error occurred while saving data: {e}")

    def fetch_and_display_data(self):
        # Clear treeview
        for item in self.data_treeview.get_children():
            self.data_treeview.delete(item)
        # Clear markers
        for marker in self.marker_mapping.values():
            marker.delete()
        self.marker_mapping = {}
        self.markers = {}
        try:
            docs = db.collection('user_feedback').stream()
            for doc in docs:
                data = doc.to_dict()
                doc_id = doc.id
                # Parent items
                parent_id = self.data_treeview.insert('', 'end', iid=doc_id, text=data['name'],
                                                      values=(data['address'],))
                # Child items
                self.data_treeview.insert(parent_id, 'end', text='Rating', values=(data['rating'],))
                self.data_treeview.insert(parent_id, 'end', text='Comments', values=(data['comments'],))

                # Add marker to map
                lat = data.get('latitude')
                lon = data.get('longitude')
                if lat is not None and lon is not None:
                    try:
                        marker = self.map_widget.set_marker(float(lat), float(lon), text=data['name'])
                        # Map marker to document ID
                        self.marker_mapping[doc_id] = marker
                        self.markers[marker] = doc_id
                        # Bind click event to marker
                        # no left click callback for tkintermapview
                        # marker.add_left_click_callback(self.marker_click_event)
                    except Exception as e:
                        print(f"Error setting marker for '{data['name']}': {e}")
        except Exception as e:
            print(f"An error occurred while fetching data: {e}")

    def remove_destination_by_id(self, doc_id):

        # Remove from database
        try:
            db.collection('user_feedback').document(doc_id).delete()
        except Exception as e:
            print(f"Error deleting document: {e}")
        # Remove from map
        marker = self.marker_mapping.get(doc_id)
        if marker:
            marker.delete()
            del self.marker_mapping[doc_id]
            del self.markers[marker]
        # Remove from list
        self.data_treeview.delete(doc_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = MapDisplayApp(root)
    root.mainloop()
